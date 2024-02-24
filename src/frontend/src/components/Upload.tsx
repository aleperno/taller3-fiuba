/*
    Cheat Sheet:
        - https://dev.to/alecgrey/controlled-forms-with-front-and-backend-validations-using-react-bootstrap-5a2
*/

import React, { useEffect, useState } from 'react';
import { useNavigate } from "react-router-dom";

import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';
import * as Icon from 'react-bootstrap-icons';


import "./Upload.css";

import Header from './common/header'
import DragAndDrop from "./common/DragDropFrile";

class MyForm {
    file_name: string;
    compress: boolean;
    privacy: string;
    convert_latex: boolean;
    shared_emails?: string[];
    colours?: number;
    white_background?: boolean;
    file_b64?: string;
    

    constructor(colours: number = 5, compress: boolean = false, white_background: boolean = false, privacy: string = "private") {
        // Mandatory fields
        this.file_name = "";
        this.compress = compress;
        this.privacy = privacy;
        this.file_b64 = ""
        this.convert_latex = false;

        // Optional field
        this.shared_emails = [];

        // Mandatory if compress
        this.colours = colours;
        this.white_background = white_background;
    }
}

type Errors = {
    colours?: string;
    shared_emails?: string;
    file_name?: string;
}

interface Map {
    [key: string]: string | undefined
  }
  

interface UploadProps {
    setCurrentTasksLoaded: React.Dispatch<React.SetStateAction<boolean>>;
}


const Upload: React.FC<UploadProps> = ({setCurrentTasksLoaded}) => {
    const navigate = useNavigate();
    const [uploaded, setUploaded] = useState(false);
    const [fileUrl, setFileUrl] = useState<string | null>(null);
    const [fileName, setFileName] = useState<string>("");
    const [fileB64, setFileB64] = useState<string | null>(null);
    const [compressCheckboxStatus, setCompressCheckboxStatus] = useState(false);

    const [ form, setForm ] = useState(new MyForm())
    const [ errors, setErrors ] = useState<Errors>({})
    const [ isRestricted, setRestricted] = useState(false);
    const [ sharedMails, setSharedMails] = useState<string[]>([]);
    const [ sharedMailsInput, setSharedMailsInput] = useState<string>("");

    const setField = (field: string, value: any) => {
        setForm({
          ...form,
          [field]: value
        })
        //setUno(3, () => {console.log("El uno es: ", uno)});
        /*
        let myErrorObj : Map = {...errors};
        console.log("Chequeo... " + myErrorObj[field])
        if ( !!myErrorObj[field] ) {
            //Nothing
            setErrors({
                ...errors,
                [field]: null
            })
        }
        */
        console.log("Nuevo valor de ", field, " es: ", value);
        //const newErrors = findFormErrors();
        //console.log("Los nuevos errores son: ", newErrors);
        //setErrors(newErrors);
      }

    
    const format_form = () => {
        /*
            Formats form for what the API expects
        */
        let formatted_form = {...form}

        // Delete shared emails if privacy is not restricted
        if (formatted_form.privacy !== 'restricted') {
            delete formatted_form.shared_emails;
        } else {
            formatted_form.shared_emails = sharedMailsInput.split(",");
        }

        // Delete colours and white background if compress is false
        if (!formatted_form.compress) {
            delete formatted_form.colours;
            delete formatted_form.white_background;
        }

        // Show formatted form
        console.log("El formateado es: ", formatted_form);
        return formatted_form;
    }


    const findFormErrors = () => {
        const { colours, file_name } = form
        const newErrors : {[k: string]: any} = {}
        // rating errors
        if ( !colours || colours > 999 || colours < 1 ) newErrors.colours = 'Debe ingresar un valor entre 1 y 999'
        if ( !colours || !Number.isInteger(Number(colours)) ) newErrors.colours = 'Debe ingresar un valor entero'
        //if ( sharedMailsInput === "") newErrors.shared_emails = 'Debe ingresar al menos un email'
        if ( !file_name ) newErrors.file_name = 'Debe ingresar un nombre'
        return newErrors
    }

    const validateFormPeSubmit = () => {
        const newErrors = findFormErrors();
        if ( isRestricted && sharedMailsInput === "") newErrors.shared_emails = 'Debe ingresar al menos un email'
        if ( isRestricted && sharedMailsInput !== "" && !validateEmails() ) newErrors.shared_emails = 'Verifique los emails ingresados'
        return newErrors
    }

    const validateEmails = () => {
        let res = true;
        //const emailRegex = new RegExp("^[^\s@]+@[^\s@]+\.[^\s@]+$")
        const emailRegex = new RegExp("^[a-zA-Z0-9_.-]+@([a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]+$")
        const emailArray = sharedMailsInput.split(",");

        emailArray.forEach((email) => {
            const valiedEmail = email.match(emailRegex);
            if (!valiedEmail) {
                console.log("Email invalido detectado: ", email);
                res = false;
            }
        });

        return res
    }

    useEffect(() => {
        console.log("Detecte cambio en el form");
        const newErrors = findFormErrors();
        setErrors(newErrors);
    }, [form]);

    const handleSubmit = async (e: any) => {
        console.log("Apreto subir apunte");
        e.preventDefault()
        // get our new errors
        //const newErrors = findFormErrors()
        const newErrors = validateFormPeSubmit();
        // Conditional logic:
        if ( Object.keys(newErrors).length > 0 ) {
            // We got errors!
            console.log("Obtuve errores!: ", newErrors);
            setErrors(newErrors)
        } else {
            // No errors! Put any logic here for the form submission!
            console.log("El form vale: ", form);
            const request_body = format_form();
            //alert('Thank you for your feedback!')
            console.log("Enviado")
            const response = await fetch('http://localhost:8080/uploadfile',
                {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(request_body)
                });
            if (response.ok) {
                setCurrentTasksLoaded(false);
                navigate(`/tasks`);
            } else {
                alert("Hubo un error al subir el archivo");
            }
        }
      }

    const handleMailInputChange = (event: any) => {
        const filteredValue = event.target.value.replace(/[\r\n\v\s]+/g, '');
        if (filteredValue != "" && errors.shared_emails) {
            const newErrors : {[k: string]: any} = {...errors}
            delete newErrors.shared_emails;
            setErrors({
                ...newErrors
            })
        }
        setSharedMailsInput(filteredValue);
    }


    useEffect(() => {
        console.log("Detecte un cambio en el file desde el padre. El estado es: " + uploaded);
        console.log("El fileUrl es: " + fileUrl);
        if (fileUrl) {
            const b64 = fileUrl.replace(/^data:application\/pdf;base64,/g, "")
            setFileB64(b64);
            setForm({...form, file_name: fileName, file_b64: b64})
            console.log("El base64 del archivo es: " + b64);
        }
    }, [uploaded]);

    const renderTooltip = (props: any) => (
        <Tooltip id="button-tooltip" {...props}>
          Simple tooltip
        </Tooltip>
      );

    return (
        <div>
            <Header/>
            <h4>Aca dare la opcion de upload</h4>
            { !uploaded && (
                <div>
                <DragAndDrop setUploaded={setUploaded} setFileUrl={setFileUrl} fileUrl={fileUrl} setFileName={setFileName}/>
                </div>
            )
}
            { uploaded && fileUrl && (
                <div className="uploaded-centered-container">
                    <div className="pdf-viewer">
                    <embed
                        src={fileUrl}
                        type="application/pdf"
                        width="100%"
                        height="100%"
                    />
                    </div>
                    <div className="pdf-options-container">
                        <Form>
                        <Form.Group as={Row} className="mb-3">
                                    <Form.Label column sm={2}>Nombre</Form.Label>
                                    <Col sm={7}>
                                        <Form.Control
                                            type="email"
                                            placeholder="Ingrese emails"
                                            value={form.file_name}
                                            onChange={(e)=>{setField('file_name', e.target.value)}}
                                            isInvalid={!!errors.file_name}
                                        />
                                        {!!errors.file_name && (
                                            <Form.Control.Feedback type='invalid'>
                                                {errors.file_name}
                                            </Form.Control.Feedback>
                                        )
                                        }
                                    </Col>
                                    
                                </Form.Group>


                            <Row className="mb-3">
                            <Form.Group className="mb-3" controlId="formBasicCheckbox" as={Col}>
                                
                                <Form.Check type="switch" label="Comprimir" checked={compressCheckboxStatus}
                                            onChange={(e) => {console.log("Chequeo quiero comprimir");
                                                              setCompressCheckboxStatus(e.target.checked);
                                                              setField('compress', e.target.checked)}}/>
                                
                            </Form.Group>
                                <Col>
                                    <OverlayTrigger
                                        placement="right"
                                        delay={{ show: 250, hide: 400 }}
                                        overlay={(props: any) => {
                                            return (
                                                <Tooltip id="button-tooltip" {...props}>
                                                    <p>Se empleará procesamiento de imágenes para reducir el tamaño del archivo.</p>
                                                    <p>Es posible que la calidad del archivo se vea afectada</p>
                                                </Tooltip>
                                            )
                                        
                                        }}
                                    >
                                        <Icon.InfoCircle />
                                    </OverlayTrigger>
                                </Col>
                            </Row>


                            
                            { compressCheckboxStatus && (
                                <div>
                                    <Row className="mb-3">
                                        <Form.Group as={Col} className="mb-3" controlId="formBasicCheckbox">
                                            <Form.Check type="switch" label="Fondo en Blanco"
                                                         onChange={(e) => {setField('white_background', e.target.checked)}}/>
                                        </Form.Group>
                                        <Col>
                                    <OverlayTrigger
                                        placement="right"
                                        delay={{ show: 250, hide: 400 }}
                                        overlay={(props: any) => {
                                            return (
                                                <Tooltip id="button-tooltip" {...props}>
                                                    <p>Se intentará dejar el fondo del archivo en blanco para mejor lectura</p>
                                                    <p>Esta opción puede lograr mejor resultado de compresión (menor tamaño)</p>
                                                </Tooltip>
                                            )
                                        
                                        }}
                                    >
                                        <Icon.InfoCircle />
                                    </OverlayTrigger>
                                </Col>
                                    </Row>

                                        <Form.Group as={Row}>
                                            <Form.Label column sm={3}>Colores</Form.Label>
                                            <Col sm={3}>
                                            <Form.Control
                                                type='number'
                                                onChange={e => setField('colours', e.target.value)}
                                                isInvalid={!!errors.colours}
                                                value={form.colours}
                                            />
                                            <Form.Control.Feedback type='invalid'>
                                            {errors.colours}
                                        </Form.Control.Feedback>
                                            </Col>
                                            <Col>
                                    <OverlayTrigger
                                        placement="right"
                                        delay={{ show: 250, hide: 400 }}
                                        overlay={(props: any) => {
                                            return (
                                                <Tooltip id="button-tooltip" {...props}>
                                                    <p>Cantidad de colores totales del archivo comprimido</p>
                                                    <p>A mayor número, mejor definición pero mayor tamaño</p>
                                                </Tooltip>
                                            )
                                        
                                        }}
                                    >
                                        <Icon.InfoCircle />
                                    </OverlayTrigger>
                                </Col>
                                        </Form.Group>
                                </div>
                                )
                            }
                            <Form.Group as={Row} className="mb-3">
                                <Form.Label column sm={3} >Privacidad</Form.Label>
                                <Col sm={5} >
                                    <Form.Select aria-label="Default select example"
                                        onChange={(e) => {
                                            setField('privacy', e.target.value);
                                            setRestricted(e.target.value === 'restricted');
                                        }}>
                                        <option value="private">Privado</option>
                                        <option value="restricted">Restringido</option>
                                        <option value="public">Publico</option>
                                    </Form.Select>
                                </Col>
                                <Col sm={2}>
                                    <OverlayTrigger
                                        placement="right"
                                        delay={{ show: 250, hide: 400 }}
                                        overlay={(props: any) => {
                                            return (
                                                <Tooltip id="button-tooltip" {...props}>
                                                    <ul>
                                                        <li>Privado: Solo tu tendrás acceso al apunte</li>
                                                        <li>Restringido: El acceso estará limitado a las cuentas de e-mail que tu definas</li>
                                                        <li>Público: El apunte será público</li>
                                                    </ul>

                                                    <p>La privacidad puede cambiarse luego de subido el apunte</p>
                                                </Tooltip>
                                            )
                                        
                                        }}
                                    >
                                        <Icon.InfoCircle />
                                    </OverlayTrigger>
                                </Col>
                            </Form.Group>
                            {isRestricted && (
                                <div>
                                <Form.Group as={Row} className="mb-3">
                                    <Form.Label column sm={2}>Compartirle a</Form.Label>
                                    <Col sm={7}>
                                        <Form.Control
                                            type="email"
                                            placeholder="Ingrese emails"
                                            value={sharedMailsInput}
                                            onChange={handleMailInputChange}
                                            as="textarea"
                                            rows={2}
                                            style={{resize: 'none', overflow:'auto'}}
                                            isInvalid={!!errors.shared_emails}
                                        />
                                        {!!errors.shared_emails && (
                                            <Form.Control.Feedback type='invalid'>
                                                {errors.shared_emails}
                                            </Form.Control.Feedback>
                                        ) || (
                                            <Form.Text className="text-muted">
                                            Puede ingresar múltiples cuentas de email, separadas por coma.
                                        </Form.Text>
                                        )
                                        }
                                    </Col>
                                    
                                </Form.Group>
                                </div>
                            )}
                            <Row className="mb-3">
                                <Form.Group className="mb-3" controlId="formBasicCheckbox" as={Col}>

                                    <Form.Check type="switch" label="Convertir a Latex" checked={form.convert_latex}
                                        onChange={(e) => {
                                            //console.log("Chequeo quiero comprimir");
                                            //setCompressCheckboxStatus(e.target.checked);
                                            setField('convert_latex', e.target.checked)
                                        }} />

                                </Form.Group>
                                <Col>
                                    <OverlayTrigger
                                        placement="right"
                                        delay={{ show: 250, hide: 400 }}
                                        overlay={(props: any) => {
                                            return (
                                                <Tooltip id="button-tooltip" {...props}>
                                                    <p>Desea convertir el apunte a Latex?</p>
                                                    <p>De haber seleccionado comprimir el archivo, la conversión se hará en base a dicho archivo.
                                                        De lo contrario se hará en base al original.
                                                    </p>
                                                </Tooltip>
                                            )

                                        }}
                                    >
                                        <Icon.InfoCircle />
                                    </OverlayTrigger>
                                </Col>
                            </Row>
                            <Button variant="primary" onClick={handleSubmit}>
                                Subir Apunte
                            </Button>
                        </Form>
                    </div>
                </div>
            )
            }
        </div>
    )
}

export default Upload;