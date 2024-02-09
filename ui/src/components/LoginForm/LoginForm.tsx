import { useState } from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Link from '@mui/material/Link';
import Box from '@mui/material/Box';
import { useAppContext } from '../App/AppContext';
import { Typography } from '@mui/material';
import { isServerError } from '../../utils/apiAuthRequests';

const LoginForm = () => {
    const appContext = useAppContext();
    const [loggingIn, setLoggingIn] = useState(false);

    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });

    const [errors, setErrors] = useState({
        username: '',
        password: '',
        request: '',
    });

    const validateForm = () => {
        let valid = true;
        const newErrors = { username: '', password: '', request: '' };

        if (!formData.username) {
            newErrors.username = 'Username is required';
            valid = false;
        }

        if (!formData.password) {
            newErrors.password = 'Password is required';
            valid = false;
        }

        setErrors(newErrors);
        return valid;
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setLoggingIn(true);

        const loginResponse = await appContext.appLogin(
            formData.username,
            formData.password
        );

        if (isServerError(loginResponse)) {
            setErrors({
                username: '',
                password: '',
                request: loginResponse.errorMessage,
            });
        }

        setLoggingIn(false);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, checked } = e.target;
        setFormData({
            ...formData,
            [name]: name === 'rememberMe' ? checked : value,
        });
    };

    return (
        <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            minHeight="100vh"
        >
            <Box
                component="form"
                onSubmit={handleSubmit}
                sx={{
                    maxWidth: '500px',
                    margin: 'auto',
                    padding: '20px',
                    borderRadius: '8px',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                    backgroundColor:
                        appContext?.theme?.palette.mode === 'light'
                            ? 'white'
                            : '#0c1416',
                }}
            >
                <Typography variant="h4" component="h2" gutterBottom>
                    TESLA: Login
                </Typography>
                <Typography component="p" gutterBottom>
                    Tools Enabled Safely and Library Access
                </Typography>
                {errors.request && (
                    <Typography component="p" color="error" gutterBottom>
                        {errors.request}
                    </Typography>
                )}
                <TextField
                    fullWidth
                    label="Username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    error={Boolean(errors.username)}
                    helperText={errors.username}
                    margin="normal"
                    disabled={loggingIn}
                />
                <TextField
                    fullWidth
                    type="password"
                    label="Password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    error={Boolean(errors.password)}
                    helperText={errors.password}
                    margin="normal"
                    disabled={loggingIn}
                    sx={{ mt: 2 }}
                />
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    fullWidth
                    disabled={loggingIn}
                    sx={{ mt: 2 }}
                >
                    {loggingIn ? 'Logging in...' : 'Login'}
                </Button>
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                    <Box mt={1}>
                        <Link href="/register">
                            Don't have an account? Sign Up
                        </Link>
                    </Box>
                </Box>
            </Box>
        </Box>
    );
};

export default LoginForm;
