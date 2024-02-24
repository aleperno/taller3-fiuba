import { useQuery } from "react-query";

import { useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import Header from './components/common/header';
import Button from 'react-bootstrap/Button';

interface BeResponse {
  name: string;
}

interface BeError {
  message: string
}



function Home(props: any) {
  const location = useLocation();

  useEffect(() => {
    console.log("User is back home");
  }, [location]);

  return (
    <div>
      <Header/>
      <Button onClick={() => { console.log("e mono");}}>actualizame</Button>
      <p>Esta es la pantalla principal</p>
    </div>
  );
}


export default Home;