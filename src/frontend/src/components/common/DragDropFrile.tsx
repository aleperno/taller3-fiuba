import React, { useState } from 'react';

import './DragDropFile.css';

interface DragAndDropProps {
    setUploaded: React.Dispatch<React.SetStateAction<boolean>>,
    fileUrl: string | null,
    setFileUrl: React.Dispatch<React.SetStateAction<string | null>>
    setFileName: React.Dispatch<React.SetStateAction<string>>
  }

const DragAndDrop: React.FC<DragAndDropProps> = ({setUploaded, setFileUrl, fileUrl, setFileName}) => {
    const [dragging, setDragging] = useState(false);
  
    const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setDragging(true);
    };
  
    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setDragging(false);
    };
  
    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
    };
  
    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
  
      setDragging(false);
  
      const file = e.dataTransfer.files[0];
      if (!file || file.type !== 'application/pdf') {
        alert('Please select a PDF file.');
        return;
      }
  
      const fileReader = new FileReader();
      fileReader.onload = (event) => {
        if (event.target) {
          setFileUrl(event.target.result as string);
          setUploaded(true);
        }
      };
      fileReader.readAsDataURL(file);
      setFileName(file.name.replace(/\.pdf$/, '')); // Remove .pdf extension
      //setUploaded(true);
    };
  
    const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files && e.target.files[0];
      if (!file || file.type !== 'application/pdf') {
        alert('Please select a PDF file.');
        return;
      }
  
      const fileReader = new FileReader();
      fileReader.onload = (event) => {
        if (event.target) {
          setFileUrl(event.target.result as string);
          setUploaded(true);
        }
      };
      fileReader.readAsDataURL(file);
      console.log("subo archivo: ", file);
      setFileName(file.name.replace(/\.pdf$/, '')); // Remove .pdf extension
    };
  
    return (
    <div className="centered-container">
      <div
        className={`drag-drop-zone ${dragging ? 'active' : ''}`}
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          style={{ display: 'none' }}
          onChange={handleFileInputChange}
          accept=".pdf"
          id="fileInput"
        />
        <label htmlFor="fileInput" className="full-area-label">
          <p>Drag & Drop PDF file here or click to browse</p>
        </label>
      </div>
      </div>
    );
  };
  
  export default DragAndDrop;