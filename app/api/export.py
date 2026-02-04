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
    db: Session = Depends(get_db),
    ocs_db: Session = Depends(get_ocs_db)
):
    # 1. Fetch Local Data with Floor Name
    nodes = db.query(NetworkNode, Floor).outerjoin(Floor, NetworkNode.floor_id == Floor.id).all()
    
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
            "IP (Netmap)": node.ip_address,
            # OCS Defaults
            "OCS IP": None,
            "OCS Processador": None,
            "OCS Memória (MB)": None,
            "OCS OS": None,
            "OCS Usuário": None,
            "OCS Última Sincronização": None
        }
        
        # 3. Enrich with OCS Data if it's a computer
        if node.type == 'Computador' and ocs_db:
            ocs_info = get_machine_info(node.name, ocs_db)
            if ocs_info:
                row["OCS IP"] = ocs_info.get("IPADDR")
                row["OCS Processador"] = ocs_info.get("PROCESSORT")
                row["OCS Memória (MB)"] = ocs_info.get("MEMORY")
                row["OCS OS"] = ocs_info.get("OSNAME")
                row["OCS Usuário"] = ocs_info.get("USERID")
                row["OCS Última Sincronização"] = ocs_info.get("LASTDATE")
        
        data.append(row)
        
    # 4. Generate DataFrame
    df = pd.DataFrame(data)
    
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
