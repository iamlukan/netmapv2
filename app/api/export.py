from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.ocs import get_ocs_db
from app.models.node import NetworkNode
from app.models.floor import Floor
from app.api.ocs import get_machine_info
import pandas as pd
import io
from datetime import datetime

router = APIRouter()

@router.get("/export/excel")
def export_nodes_excel(
    types: str = None, # Comma separated: 'Computador,Ramal'
    fields: str = None, # Comma separated: 'name,ip_address'
    db: Session = Depends(get_db),
    ocs_db: Session = Depends(get_ocs_db)
):
    # Filter by Types
    query = db.query(NetworkNode, Floor).outerjoin(Floor, NetworkNode.floor_id == Floor.id)
    
    if types:
        type_list = [t.strip() for t in types.split(',')]
        query = query.filter(NetworkNode.type.in_(type_list))
    
    nodes = query.all()
    
    data = []
    
    # 2. Process each node
    for node, floor in nodes:
        row = {
            "ID": node.id,
            "Nome": node.name,
            "Tipo": node.type,
            "Andar": floor.name if floor else f"Desconhecido ({node.floor_id})",
            "Ponto de Rede": node.point_number,
            "Responsável": node.assigned_to,
            "Detalhes": node.details,
            "IP (Netmap)": node.ip_address,
            # OCS Defaults
            "OCS IP": None,
            "OCS Processador": None,
            "OCS Memória (MB)": None,
            "OCS Disco (MB)": None,
            "OCS OS": None,
            "OCS Usuário": None,
            "OCS Última Sincronização": None
        }
        
        # 3. Enrich with OCS Data if it's a computer
        if node.type == 'Computador' and ocs_db:
            ocs_info = get_machine_info(node.name, ocs_db)
            if ocs_info:
                row["OCS IP"] = ocs_info.get("IPADDR")
                row["OCS Processador"] = ocs_info.get("PROCESSOR") # Fix key name from PROCESSORT to PROCESSOR as per service alias
                row["OCS Memória (MB)"] = ocs_info.get("MEMORY")
                row["OCS Disco (MB)"] = ocs_info.get("DISKSIZE")
                row["OCS OS"] = ocs_info.get("OSNAME")
                row["OCS Usuário"] = ocs_info.get("USERID")
                row["OCS Última Sincronização"] = ocs_info.get("LASTDATE")
        
        data.append(row)
        
    # 4. Generate DataFrame
    df = pd.DataFrame(data)
    
    # 5. Filter Columns if requested
    if fields and not df.empty:
        # Map Frontend Field names to DataFrame Columns
        field_map = {
            "name": "Nome",
            "type": "Tipo",
            "floor": "Andar",
            "point": "Ponto de Rede",
            "assigned": "Responsável",
            "details": "Detalhes",
            "ip": "IP (Netmap)",
            "ocs_ip": "OCS IP",
            "ocs_cpu": "OCS Processador",
            "ocs_ram": "OCS Memória (MB)",
            "ocs_disk": "OCS Disco (MB)",
            "ocs_os": "OCS OS",
            "ocs_user": "OCS Usuário",
            "ocs_last": "OCS Última Sincronização"
        }
        
        requested_cols = []
        # Always include ID? Maybe not if user wants clean list.
        # Let's include ID only if implicit or requested? Let's stick to user request.
        
        req_fields = [f.strip() for f in fields.split(',')]
        for rf in req_fields:
            if rf in field_map:
                requested_cols.append(field_map[rf])
        
        # Filter DF
        existing_cols = [c for c in requested_cols if c in df.columns]
        if existing_cols:
            df = df[existing_cols]
    
    # 5. Create Excel in Memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventario')
        
    output.seek(0)
    
    # 6. Return Streaming Response
    filename = f"netmap_export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    
    return StreamingResponse(
        output, 
        headers=headers, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
