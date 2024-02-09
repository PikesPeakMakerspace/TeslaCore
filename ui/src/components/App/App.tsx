import React from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
import TopNav from '../TopNav/TopNav';
import AccessCards from '../AccessCards/AccessCards';
import AccessNodes from '../AccessNodes/AccessNodes';
import Devices from '../Devices/Devices';
import Reports from '../Reports/Reports';
import Users from '../Users/Users';
import AdminDashboard from '../AdminDashboard/AdminDashboard';
import { ThemeProvider } from '@mui/material/styles';
import { Box, Container } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { useAppContext } from './AppContext';
import LoginForm from '../LoginForm/LoginForm';
import backgroundImg from './background.png';
import Logout from '../Logout/Logout';

export default function App() {
    const appContext = useAppContext();

    if (!appContext.theme || appContext.loading) {
        return <></>;
    }

    let routedContent;
    if (appContext.loggedIn) {
        // access logged in routed content
        routedContent = (
            <>
                <TopNav />
                <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                    <Routes>
                        <Route path="/" element={<AdminDashboard />} />
                        <Route path="/users" element={<Users />} />
                        <Route path="/users/:id" element={<Users />} />
                        <Route path="/accessCards" element={<AccessCards />} />
                        <Route
                            path="/accessCards/:id"
                            element={<AccessCards />}
                        />
                        <Route path="/devices" element={<Devices />} />
                        <Route path="/devices/:id" element={<Devices />} />
                        <Route path="/accessNodes" element={<AccessNodes />} />
                        <Route
                            path="/accessNodes/:id"
                            element={<AccessNodes />}
                        />
                        <Route path="/reports" element={<Reports />} />
                        <Route
                            path="/reports/accessCardEdits"
                            element={<Reports />}
                        />
                        <Route
                            path="/reports/deviceAccess"
                            element={<Reports />}
                        />
                        <Route
                            path="/reports/userEdits"
                            element={<Reports />}
                        />
                        <Route
                            path="/reports/userAccess"
                            element={<Reports />}
                        />
                        <Route path="/logout" element={<Logout />} />
                    </Routes>
                </Container>
            </>
        );
    } else {
        // access login/register content
        routedContent = (
            <Container>
                <Routes>
                    <Route
                        path="/register"
                        element={<>Register here soon.</>}
                    />
                    <Route path="/" element={<LoginForm />} />
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </Container>
        );
    }

    return (
        <>
            <ThemeProvider theme={appContext.theme}>
                <CssBaseline />
                <Box
                    component="main"
                    sx={{
                        backgroundColor: (theme) =>
                            theme.palette.mode === 'light'
                                ? '#e8f2f5'
                                : '#0f1a1c',
                        backgroundImage: appContext.loggedIn
                            ? undefined
                            : `url(${backgroundImg})`,
                        flexGrow: 1,
                        height: '100vh',
                        overflow: 'auto',
                    }}
                >
                    {routedContent}
                </Box>
            </ThemeProvider>
        </>
    );
}
