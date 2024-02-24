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
import { execArgv } from 'process';

/*
interface TaskOptions {
      upload: boolean;
      compress: boolean;
      convert: boolean;
      build: boolean;
}

interface SubTaskData {
  status: string,
  progress: number,
  created_at: string,
  last_updated: string
}

interface SubTasksData {
    upload?: SubTaskData,
    compress?: SubTaskData,
    convert?: SubTaskData,
    build?: SubTaskData
}
*/
// AAAA

interface SubTaskDataType {
  status: string,
  progress: number,
  created_at: string,
  last_updated: string | null
}

interface TasksDataType {
  file_name: string,
  status: string,
  created_at: string,
  last_updated: string | null
  upload?: SubTaskDataType,
  compress?: SubTaskDataType,
  convert_latex?: SubTaskDataType,
  build_latex?: SubTaskDataType
}

interface AllTasksDataType {
  [key: string]: TasksDataType;
}

interface TaskDataInArray extends TasksDataType {
  id: string
}

const testData = {
  "12080d98-52f7-4588-9bb5-a61472e755a1": {
      "file_name": "Alejandro Pernin CV",
      "status": "pending",
      "created_at": "2024-01-31T23:25:26.160087+00:00",
      "last_updated": null,
      "upload": {
          "progress": 0,
          "status": "pending",
          "created_at": "2024-01-31T23:25:26.167380+00:00",
          "last_updated": null
      }
  },
  "8178971e-9a3e-4cdc-bcf8-94dbf96f6769": {
      "file_name": "Alejandro Pernin CV",
      "status": "pending",
      "created_at": "2024-01-31T23:25:32.509356+00:00",
      "last_updated": null,
      "upload": {
          "progress": 0,
          "status": "pending",
          "created_at": "2024-01-31T23:25:32.513739+00:00",
          "last_updated": null
      }
  }
}

// Sample data
/*
  const data = [
    { id: 1, file_name: 'Quimica', status: 'pending', created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'},
    { id: 2, file_name: 'Fisica', status: 'in_progress', created_at: '2023-12-25 23:00:10', last_updated: '2024-01-12 22:00:05'},
    { id: 3, file_name: 'Matematica', status: 'error', created_at: '2023-12-26 23:00:10', last_updated: '2024-01-12 22:00:05'},
    { id: 4, file_name: 'Algebra', status: 'done', created_at: '2023-12-27 23:00:10', last_updated: '2024-01-12 22:00:05'},
  ];

  const taskOptions: {[taskId: number]: TaskOptions} = {
    1: {upload: true, compress: false, convert: false, build: false},
    2: {upload: true, compress: true, convert: false, build: false},
    3: {upload: true, compress: true, convert: true, build: false},
    4: {upload: true, compress: true, convert: true, build: true},
  }

const subTaskData: {[taskId: number]: SubTasksData} = {
    1: {
        upload: {status: 'done', progress: 1, created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'},
    },
    2: {
        upload: {status: 'done', progress: 2, created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'},
        compress: {status: 'done', progress: 3, created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'},
    },
    3: {
        upload: {status: 'done', progress: 4, created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'},
        compress: {status: 'done', progress: 5, created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'},
        convert: {status: 'done', progress: 69, created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'},
    },
    4: {
        upload: {status: 'done', progress: 69, created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'},
        compress: {status: 'error', progress: 69, created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'},
        convert: {status: 'done', progress: 69, created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'},
        build: {status: 'done', progress: 69, created_at: '2023-12-24 23:00:10', last_updated: '2024-01-12 22:00:05'}
    }
}
*/

const statusMapping = {
    pending: 'Pendiente',
    in_progress: 'En Progreso',
    done: 'Finalizado',
    error: 'Error',
}


const badgeMapping = {
    pending: 'warning',
    in_progress: 'primary',
    done: 'success',
    error: 'danger',
}


const taskMapping = {
    upload: 'Subir',
    compress: 'Comprimir',
    convert_latex: 'Convertir a LaTeX',
    build_latex: 'Compilar LaTeX'
}

interface BeResponse {
  name: string;
}

interface BeError {
  message: string
}

interface TasksProps {
    myVar: AllTasksDataType;
    setMyVar: Dispatch<SetStateAction<AllTasksDataType>>;
    currentTasksLoaded: boolean;
    setCurrentTasksLodaded: Dispatch<SetStateAction<boolean>>;
}


//function Tasks(currentData2: AllTasksDataType) {
const Tasks: React.FC<TasksProps> = ({myVar, setMyVar, currentTasksLoaded, setCurrentTasksLodaded}) => {
    const [filter, setFilter] = useState('');
    //const [expandedRow, setExpandedRow] = useState(null);
    const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
    const location = useLocation();
    const currentData = myVar;
    const setCurrentData = setMyVar;
    //const [currentData, setCurrentData] = useState<AllTasksDataType>({});
    const [dataArray, setDataArray] = useState<TaskDataInArray[]>([])

    useEffect(() => {
        console.log("Las location was: ", location.pathname)
        if (!currentTasksLoaded) {
            console.log("Cargo tasks xq no veo que esten cargados")
            refetch();
        }
    }, [location]);

    const {isLoading, error, data, refetch} = useQuery<AllTasksDataType, BeError>(['get-tasks'], () => 
        fetch('http://localhost:8080/mytasks', {credentials: 'include', headers: {'Content-Type': 'application/json',
        'Accept': 'application/json',
        },}).then((res) => {return res.json();}),{refetchOnWindowFocus: false, staleTime: 15 * 6e4, onSuccess: (data) => {console.log("obtuve como res: ", data); setCurrentData({...data}); setCurrentTasksLodaded(true)}});

    
    const handleRowClick = (index:any) => {
      console.log("Clickeo en la fila: " + index)
      console.log("Expanded rows actual:" + Array.from(expandedRows))
      if (!expandedRows.has(index)) {
        //setExpandedRow(null); // Collapse if already expanded
        expandedRows.add(index);
      } else {
        //setExpandedRow(index);
        expandedRows.delete(index);
      }
      setExpandedRows(new Set(expandedRows));
      console.log("Expanded rows final:" + Array.from(expandedRows))
    };

    /*
    const getTaskOption = (taskId: number, taskName: string) => {
        return taskOptions[taskId as number][taskName as keyof TaskOptions];
    }

    const getSubTaskData = (taskId: number, taskName: string) => {
        let res = subTaskData[taskId as number][taskName as keyof SubTasksData];
        console.log(res);
        return res
    }
    */
    const getSubTaskDataRender = (index:any, subTaskData: TaskDataInArray) => {
        const taskList = ["upload", "compress", "convert_latex", "build_latex"];
        //const taskList = ["upload"];
        return (
            <tbody>
                {taskList.map((taskName, index) => (
                    // Checkeo si la tarea especifica esta habilitada en la subtask
                    //getTaskOption(taskId, taskName)? (
                    subTaskData[taskName as keyof TaskDataInArray]?(
                    <tr key={index}>
                        <td>{taskMapping[taskName as keyof typeof taskMapping]}</td>
                        {
                            // Veo el estado de la subtask
                            //getSubTaskData(taskId, taskName) && (
                              1==1 && (
                                <>
                                <td>
                                    <Badge bg={badgeMapping[(subTaskData[taskName as keyof TaskDataInArray] as SubTaskDataType).status as keyof typeof statusMapping]}>
                                        {statusMapping[(subTaskData[taskName as keyof TaskDataInArray] as SubTaskDataType).status as keyof typeof statusMapping]}
                                    </Badge>
                                </td>
                                <td>
                                {(subTaskData[taskName as keyof TaskDataInArray] as SubTaskDataType).progress} 
                                </td>
                                <td>
                                    {(subTaskData[taskName as keyof TaskDataInArray] as SubTaskDataType).created_at}                         
                                </td>
                                <td>
                                    {(subTaskData[taskName as keyof TaskDataInArray] as SubTaskDataType).last_updated}                         
                                </td>
                                </>
                            )
                        }
                        <td></td>
                    </tr>
                ) : null
                ))}
            </tbody>
        )
    }
    
    const taskDataArray: TaskDataInArray[] = Object.keys(currentData as AllTasksDataType).map(id => ({
      id,
      ...(currentData as AllTasksDataType)[id]
    }));
    // filteredData
    const filtered_data = taskDataArray.filter(row => row.status.includes(filter));
    const sorted_data = taskDataArray.sort((a, b) => b.created_at.localeCompare(a.created_at));
    //const sorted_data = taskDataArray

    //console.log("Entro en la parte de tasks");
    return (
        <div>
            <Header />
            <h4>Aca muestro las tasks en proceso</h4>
            <Button onClick={() => { console.log("e mono"); refetch(); /*setExpandedRow(null)*/}}>actualizame</Button>
            <div style={{width: '80%', textAlign: 'center', margin: 'auto'}}>
            <Table striped bordered hover >
                <thead>
                    <tr>
                        <th>Nombre Archivo</th>
                        <th>Estado</th>
                        <th>Fecha Inicio</th>
                        <th>Ultima Actualización</th>
                        <th colSpan={1}>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {sorted_data.map((row, index) => (
                        <React.Fragment key={index}>
                            <tr>
                                <td>{row.file_name}</td>
                                <td>
                                    <Badge bg={badgeMapping[row.status as keyof typeof badgeMapping]}>
                                        {statusMapping[row.status as keyof typeof statusMapping]}
                                    </Badge>
                                </td>
                                <td>{row.created_at}</td>
                                
                                <td>
                                  { // Cambiar a ultima fecha actualizacion
                                    row.last_updated
                                  }
                                </td>
                            
                                <td style={{ width: "20px", textAlign: "center" }}>
                                    <Icon.InfoCircle title="Ver detalles" onClick={() => {handleRowClick(index)}}/>
                                </td>
                            </tr>
                            {/* Aca muestro las subtasks que componen la tarea */}
                            { expandedRows.has(index) && (
                                <tr>
                                    <td colSpan={5}>
                                        <Table striped bordered hover >
                                            <thead>
                                                <tr>
                                                    <th>Tarea</th>
                                                    <th>Estado</th>
                                                    <th>Progreso</th>
                                                    <th>Fecha Inicio</th>
                                                    <th>Ultima Actualización</th>
                                                    <th>Acciones</th>
                                                </tr>
                                            </thead>
                                              {
                                                getSubTaskDataRender(index, row)
                                              }
                                        </Table>
                                    </td>
                                </tr>
                            )}
                        </React.Fragment>
                    ))}
                </tbody>
            </Table>
            </div>
        </div>
    )
}

//export default Tasks;
export {Tasks, type AllTasksDataType}