import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import "@cloudscape-design/global-styles/index.css";
import { AuthProvider } from "react-oidc-context";
import App from './App';
import cognitoConfig from "./config.json"

const cognitoAuthConfig = {
  authority: cognitoConfig.authConfig.authority,
  client_id: cognitoConfig.client_id,
  redirect_uri: cognitoConfig.authConfig.redirect_uri,
  response_type: "code",
  scope: "email openid",
};

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <AuthProvider {...cognitoAuthConfig}>
      <App />
    </AuthProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
