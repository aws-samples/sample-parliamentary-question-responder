import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
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
