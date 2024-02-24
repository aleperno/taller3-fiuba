import Table from 'react-bootstrap/Table';
import Badge from 'react-bootstrap/Badge';
import Button from 'react-bootstrap/Button';
import { Link } from "react-router-dom";
import { Dispatch, SetStateAction } from "react";
import * as Icon from 'react-bootstrap-icons';

import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useQuery } from "react-query";


import Header from './common/header'
import { get } from 'http';


interface FileDataType {
  file_name: string,
  created_at: string,
  last_updated: string | null
  privacy: string
  shared_with: string
  original_url?: string
  compressed_url?: string
  latex_zip_url?: string
  latex_pdf_url?: string
}

interface AllFilesDataType {
  [key: string]: FileDataType;
}

interface FileDataInArray extends FileDataType {
  id: string
}

const statusMapping = {
    pending: 'Pendiente',
    in_progress: 'En Progreso',
    done: 'Finalizado',
    error: 'Error',
}


const privacyBadgeMapping = {
    restricted: 'warning',
    private: 'success',
    public: 'danger',
}


const privacyMapping = {
    public: 'Público',
    private: 'Privado',
    restricted: 'Restringido'
}


interface BeResponse {
  name: string;
}

interface BeError {
  message: string
}

interface TasksProps {
    currentFiles: AllFilesDataType;
    setCurrentFiles: Dispatch<SetStateAction<AllFilesDataType>>;
    currentFilesLoaded: boolean;
    setCurrentFilesLoaded: Dispatch<SetStateAction<boolean>>;
}


//function Tasks(currentData2: AllTasksDataType) {
const Files: React.FC<TasksProps> = ({currentFiles, setCurrentFiles, currentFilesLoaded, setCurrentFilesLoaded}) => {
    const [filter, setFilter] = useState('');
    const [expandedRow, setExpandedRow] = useState(null);
    const currentData = currentFiles;
    const setCurrentData = setCurrentFiles;
    const location = useLocation();
    //const [currentData, setCurrentData] = useState<AllTasksDataType>({});
    //const [dataArray, setDataArray] = useState<FileDataInArray[]>([])

    useEffect(() => {
        if (!currentFilesLoaded) {
            console.log("Cargo files xq no veo que esten cargados")
            refetch();
        }
    }, [location]);

    const {isLoading, error, data, refetch} = useQuery<AllFilesDataType, BeError>(['get-tasks'], () => 
        fetch('http://localhost:8080/myfiles', {credentials: 'include', headers: {'Content-Type': 'application/json',
        'Accept': 'application/json',
        },}).then((res) => {return res.json();}),{refetchOnWindowFocus: false, staleTime: 15 * 6e4, onSuccess: (data) => {console.log("obtuve como res: ", data); setCurrentData({...data}); setCurrentFilesLoaded(true)}});

    
    const handleRowClick = (index:any) => {
      console.log("Clickeo en la fila: " + index)
      if (expandedRow === index) {
        setExpandedRow(null); // Collapse if already expanded
      } else {
        setExpandedRow(index);
      }
    };
    
    const taskDataArray: FileDataInArray[] = Object.keys(currentData as AllFilesDataType).map(id => ({
      id,
      ...(currentData as AllFilesDataType)[id]
    }));
    // filteredData
    //const filtered_data = taskDataArray.filter(row => row.status.includes(filter));
    const sorted_data = taskDataArray.sort((a, b) => b.created_at.localeCompare(a.created_at));
    //const sorted_data = taskDataArray

    //console.log("Entro en la parte de tasks");

    const getPrivacyRender = (privacy: string) => {
        return (
            <Badge bg={privacyBadgeMapping[privacy as keyof typeof privacyBadgeMapping]}>
                {privacyMapping[privacy as keyof typeof privacyMapping]}
            </Badge>
        )
    }

    const getFileRender = (url: string | undefined, isZip: Boolean) => {
        if (url) {
            return (
                <a>
                    <Link to={url} target="_blank">
                        {
                            isZip && (
                                <Icon.FileZip size="25px" />
                            ) || <Icon.FiletypePdf size="25px"/>
                        }
                    </Link>
                </a>
            )
        }
    }

    return (
        <div>
            <Header />
            <h4>Acá muestro mis files</h4>
            <Button onClick={() => { console.log("e mono"); refetch(); /*setExpandedRow(null)*/}}>actualizame</Button>
            <div style={{width: '80%', textAlign: 'center', margin: 'auto'}}>
            <Table striped bordered hover >
                <thead>
                    <tr>
                        <th>Nombre Archivo</th>
                        <th>Original</th>
                        <th>Comprimido</th>
                        <th>Fuentes Latex</th>
                        <th>Latex PDF</th>
                        <th>Privacidad</th>
                        <th>Fecha Creacion</th>
                        <th>Ultima Actualización</th>
                        <th colSpan={1}>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {sorted_data.map((row, index) => (
                        <React.Fragment key={index}>
                            <tr>
                                <td>
                                    {row.file_name}
                                </td>
                                <td>
                                    {getFileRender(row.original_url, false)}
                                </td>
                                <td>{getFileRender(row.compressed_url, false)}</td>
                                <td>{getFileRender(row.latex_zip_url, true)}</td>
                                <td>{getFileRender(row.latex_pdf_url, false)}</td>
                                <td>{getPrivacyRender(row.privacy)}</td>
                                <td>{row.created_at}</td>
                                <td>{row.last_updated}</td>
                            
                                <td style={{ width: "20px", textAlign: "center" }}>
                                    <Icon.InfoCircle title="Ver detalles" onClick={() => {handleRowClick(index)}}/>
                                </td>
                            </tr>                            
                        </React.Fragment>
                    ))}
                </tbody>
            </Table>
            </div>
        </div>
    )
}

//export default Tasks;
export {Files, type AllFilesDataType}