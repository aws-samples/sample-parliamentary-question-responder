import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Layout from '../layout/Layout';
import Home from '../pages/Home/Home';
import GetSimilarQuestions from '../pages/GetSimilarQuestions/GetSimilarQuestions';
import { AuthContextProps } from "react-oidc-context";
import SuggestAnswers from '../pages/SuggestAnswers/SuggestAnswers';


const AppRoutes = (props: {auth: AuthContextProps}) => {

    const auth = props.auth

    return (
        <Router>
            <Routes>
                <Route element={<Layout home={true} auth={auth}/>}>
                    <Route path='/home' element={<Home />}/>
                </Route>
                <Route element={<Layout home={false} auth={auth}/>}>
                    <Route path='/similar' element={<GetSimilarQuestions auth={auth}/>} />
                    <Route path='/suggest' element={<SuggestAnswers />} />
                </Route>
                <Route index element={<Navigate to="/home" />} />
            </Routes>
        </Router>
    );
}

export default AppRoutes;