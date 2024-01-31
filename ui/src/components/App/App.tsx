import React from 'react';
import { Route, Routes } from 'react-router-dom';
import TopNav from '../TopNav/TopNav';
import AccessCards from '../AccessCards/AccessCards';
import AccessNodes from '../AccessNodes/AccessNodes';
import Devices from '../Devices/Devices';
import Reports from '../Reports/Reports';
import Users from '../Users/Users';
import AdminDashboard from '../AdminDashboard/AdminDashboard';
import { ThemeProvider } from '@mui/material/styles';
import { Box, Container, createTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { useAppContext } from './AppContext';

export default function App() {
    const appContext = useAppContext();

    return (
        <>
            <ThemeProvider theme={appContext.theme ?? createTheme()}>
                <CssBaseline />
                <Box
                    component="main"
                    sx={{
                        backgroundColor: (theme) =>
                            theme.palette.mode === 'light'
                                ? theme.palette.grey[100]
                                : theme.palette.grey[900],
                        flexGrow: 1,
                        height: '100vh',
                        overflow: 'auto',
                    }}
                >
                    <TopNav />
                    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                        <Routes>
                            <Route path="/" element={<AdminDashboard />} />
                            <Route path="/users" element={<Users />} />
                            <Route path="/users/:id" element={<Users />} />
                            <Route
                                path="/accessCards"
                                element={<AccessCards />}
                            />
                            <Route
                                path="/accessCards/:id"
                                element={<AccessCards />}
                            />
                            <Route path="/devices" element={<Devices />} />
                            <Route path="/devices/:id" element={<Devices />} />
                            <Route
                                path="/accessNodes"
                                element={<AccessNodes />}
                            />
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
                        </Routes>
                    </Container>
                </Box>
            </ThemeProvider>
        </>
    );
}
