import { useNavigate } from 'react-router-dom';
import '../../styles/landing-page.scss';
import LandingPage from "../LandingPage/LandingPage";

const Home = () => {

  const navigate = useNavigate();

  return (
    <LandingPage navigate={navigate}/>
  );
};

export default Home
