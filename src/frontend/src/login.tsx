import { useContext, useEffect, useCallback } from 'react';
import { useNavigate } from "react-router-dom";

import Button from 'react-bootstrap/Button';

import {
  MDBContainer,
  MDBRow,
  MDBCol,
}
  from 'mdb-react-ui-kit';


import {
  signOut,
  signInWithPopup,
  GoogleAuthProvider,
} from 'firebase/auth';

import './login.css';
import { AuthContext } from "./context/AuthContext";
import auth from "./firebaseSetup";
import { useCookies } from 'react-cookie';

function Login(props: any) {
  const { loggedIn, email } = props
  const navigate = useNavigate();
  const user = useContext(AuthContext);
  const [cookies, setCookie, removeCookie] = useCookies(['auth_token']);

  const onClickHandler = useCallback(() => {
    signInWithPopup(auth, new GoogleAuthProvider());
    console.log("Clicked");
  }, [auth]);

  const logoutClickChandler = () => {
    signOut(auth);
    console.log("Chau!");
  }

  const noAuth = process.env.REACT_APP_NO_API_AUTH === 'true';

  /*
  useEffect(() => {
      if (user?.currentUser) {
          let token = user.currentUser.getIdToken();
          navigate(`/home`);
      }
  }, [user]);
  */
  useEffect(() => {
    const fetchData = async () => {
      if (user?.currentUser) {
        console.log("Espero obtener el token")
        let token = await user?.currentUser.getIdToken();
        const requestBody = {
          firebase_token: token
        }

        if (noAuth) {
          console.log("No auth");
          navigate(`/home`);
          return;
        }

        const response = await fetch('http://localhost:8080/verify_token',
          {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
          },
        );

        if (response.ok) {
          const responseData = await response.json();
          console.log('Response Data:', responseData);
          const receivedCookie = response.headers.get('set-cookie');
          console.log("Headers: ", response.headers)
          console.log("Tuve una respuesta");
          if (receivedCookie) {
            console.log("Cookie recibida: ", receivedCookie);
            setCookie("auth_token", receivedCookie);
          }
          console.log("En el login el token es: " + token);
          navigate(`/home`);
        } else {
          // Must unath from firebase
          signOut(auth);
        }
       
      }
    }
    fetchData();
  }, [user]);
  /*
  return (
      <div>
          <h1>Bienvenido a Fiuba Apuntes</h1>
          <p> El usuario existe: {user ? 'si' : 'no'}</p>
          {
              user && (
                  <div>
                      <p>Nombre: {user.displayName}</p>
                      <p>Mail: {user.email}</p>
                  </div>
              )
          }
          {user === null && (
              <div className={"buttonContainer"}>
                  <input className={"inputButton"} type="button" value="Login" onClick={onClickHandler} />
              </div>
          )}
          {user != null && (<div className={"buttonContainer"}>
              <input className={"logOutButton"} type="button" value="Logout" onClick={logoutClickChandler} />
          </div>)}
      </div>
  )*/
  return (
    <MDBContainer className="my-5 gradient-form">

      <MDBRow>

        <MDBCol col='6' className="mb-5">
          <div className="d-flex flex-column ms-5">

            <div className="text-center">
              <img src="fiuba_logo.png"
                style={{ width: '185px' }} alt="logo" />
              <h4 className="mt-1 mb-5 pb-1">FIUBA Apuntes</h4>
            </div>


            <div className="text-center pt-1 mb-5 pb-1">
              <Button className="mb-4 w-50 gradient-custom-2" onClick={onClickHandler}>Ingresar</Button>
              <p>Para ingresar es necesario poseer tener un mail @fi.uba.ar</p>
            </div>
          </div>

        </MDBCol>
      </MDBRow>

    </MDBContainer>
  );
}

export default Login