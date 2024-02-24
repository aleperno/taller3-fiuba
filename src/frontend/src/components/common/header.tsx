import { useContext, useEffect, useCallback } from 'react';
import { useNavigate } from "react-router-dom";
import { AuthContext } from '../../context/AuthContext';
//import { CookiesContext } from "../../provider/CookieProvider";
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import NavbarBrand from 'react-bootstrap/NavbarBrand'

import {
  signOut,
} from 'firebase/auth';
import auth from "../../firebaseSetup";
import Cookies from 'universal-cookie';


function Header(props: any) {

  const navigate = useNavigate();
  const authC = useContext(AuthContext);
  //const cookieH = useContext(CookiesContext)
  //const authC = authContext;
  const { currentUser, hasInitialized } = authC ?? { currentUser: null, hasInitialized: false };

  const username = currentUser?.displayName ?? "";

  const logoutClickHandler = useCallback(() => {
    signOut(auth);
    console.log("Chau!");
  }, [auth]);

  useEffect(() => {
    console.log("Usuario actual: ", currentUser);
    console.log("Estado de inicialización: ", hasInitialized);
    if (!currentUser?.uid || !hasInitialized) {
      //navigate(`/`);
      //window.location.reload();
      window.open("/", "_self");
    }
  }, [currentUser, hasInitialized]);

  /*
  return (
      <div>
          <h1>Bienvenido al home!!!</h1>
          {
              user && (
                  <div>
                      <p>Nombre: {user.displayName}</p>
                      <p>Mail: {user.email}</p>
                  </div>
              )
          }
          {user != null && (<div className={"buttonContainer"}>
              <input className={"logOutButton"} type="button" value="Logout" onClick={logoutClickChandler} />
          </div>)}
      </div>
  )
  */


  return (
    <Navbar expand="lg" className="bg-body-tertiary">
      <Container>
        <NavbarBrand href="/home">
            <Nav.Link onClick={() => navigate("/home")}>
                FIUBA Apuntes
            </Nav.Link>
        </NavbarBrand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link onClick={() => navigate("/upload")}>Cargar Apunte</Nav.Link>
            <Nav.Link onClick={() => navigate(`/tasks`)} >Trabajos en Proceso</Nav.Link>
            <Nav.Link onClick={() => navigate("/files")}>Mis Apuntes</Nav.Link>
            <Nav.Link onClick={() => navigate("/shared")}>Compartidos Conmigo</Nav.Link>
          </Nav>
        </Navbar.Collapse>
        <Navbar.Collapse className="justify-content-end">
          <NavDropdown title={username} id="basic-nav-dropdown">
            <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
            <NavDropdown.Item href="#action/3.2">
              Another action
            </NavDropdown.Item>
            <NavDropdown.Item href="#action/3.3">Something</NavDropdown.Item>
            <NavDropdown.Divider />
            <NavDropdown.Item onClick={logoutClickHandler}>
              Cerrar Sesión
            </NavDropdown.Item>
          </NavDropdown>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}


export default Header;