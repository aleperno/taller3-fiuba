import React, { useContext } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';

import {AuthContext} from "./context/AuthContext";
import {Tasks, AllTasksDataType} from './components/Tasks'
import Upload from './components/Upload';
import {Files, AllFilesDataType} from './components/Files';
import {Shared, AllSharedFilesDataType} from './components/Shared';

import Login from './login';
import Home from './home';


import logo from './logo.svg';
import './App.css';

function App() {
  const [currentData, setCurrentData] = useState<AllTasksDataType>({});
  const [currentTasksLoaded, setCurrentTasksLodaded] = useState(false);
  const [currentFiles, setCurrentFiles] = useState<AllFilesDataType>({});
  const [currentFilesLoaded, setCurrentFilesLodaded] = useState(false);
  const [currentSharedFiles, setCurrentSharedFiles] = useState<AllSharedFilesDataType>({});
  const [currentSharedFilesLoaded, setCurrentSharedFilesLodaded] = useState(false);

   return (
    <div className="App">
      <BrowserRouter>
        <Routes>
         <Route path="/home" element={<Home />} />
         <Route path="/upload" element={<Upload setCurrentTasksLoaded={setCurrentTasksLodaded}/>} />
         <Route path="/files" element={<Files currentFiles={currentFiles}
                                              setCurrentFiles={setCurrentFiles}
                                              currentFilesLoaded={currentFilesLoaded}
                                              setCurrentFilesLoaded={setCurrentFilesLodaded}/>} />
         <Route path="/shared" element={<Shared currentSharedFiles={currentSharedFiles} 
                                                setCurrentSharedFiles={setCurrentSharedFiles}
                                                currentSharedFilesLoaded={currentSharedFilesLoaded}
                                                setCurrentSharedFilesLoaded={setCurrentSharedFilesLodaded}/>} />
         <Route path="/tasks" element={<Tasks myVar={currentData}
                                              setMyVar={setCurrentData}
                                              currentTasksLoaded={currentTasksLoaded}
                                              setCurrentTasksLodaded={setCurrentTasksLodaded}/>} />
         <Route path="/"  element={<Login />} />
         <Route path="*"  element={<Login />} />
        </Routes>
      </BrowserRouter>
    </div>
  )
}

export default App;
