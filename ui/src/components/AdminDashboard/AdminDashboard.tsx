import React from 'react';
import {
    Box,
    Button,
    FormControl,
    FormControlLabel,
    InputLabel,
    MenuItem,
    Select,
    Stack,
    Switch,
    TextField,
} from '@mui/material';

const AdminDashboard = () => (
    <Box>
        <h2>TESLA: Tools Enabled Safely and Library Access</h2>
        <p>Heyo!</p>
        <Stack spacing={2} direction="row" sx={{ mb: 2 }}>
            <Button variant="text">Primary</Button>
            <Button variant="contained">Primary</Button>
            <Button variant="outlined">Primary</Button>
        </Stack>
        <Stack spacing={2} direction="row" sx={{ mb: 2 }}>
            <Button variant="text" color="secondary">
                Secondary
            </Button>
            <Button variant="contained" color="secondary">
                Secondary
            </Button>
            <Button variant="outlined" color="secondary">
                Secondary
            </Button>
        </Stack>
        <Stack spacing={2} direction="row" sx={{ mb: 2 }}>
            <Button variant="text" color="error">
                Error
            </Button>
            <Button variant="contained" color="error">
                Error
            </Button>
            <Button variant="outlined" color="error">
                Error
            </Button>
        </Stack>
        <Stack spacing={2} direction="row" sx={{ mb: 2 }}>
            <Button variant="text" color="warning">
                Warning
            </Button>
            <Button variant="contained" color="warning">
                Warning
            </Button>
            <Button variant="outlined" color="warning">
                Warning
            </Button>
        </Stack>
        <Stack spacing={2} direction="row" sx={{ mb: 2 }}>
            <Button variant="text" color="info">
                Info
            </Button>
            <Button variant="contained" color="info">
                Info
            </Button>
            <Button variant="outlined" color="info">
                Info
            </Button>
        </Stack>
        <Stack spacing={2} direction="row" sx={{ mb: 2 }}>
            <Button variant="text" color="success">
                Success
            </Button>
            <Button variant="contained" color="success">
                Success
            </Button>
            <Button variant="outlined" color="success">
                Success
            </Button>
        </Stack>

        <Box>
            <h3>Hello</h3>
            <Stack spacing={2} direction="row" sx={{ mb: 2 }}>
                <FormControl fullWidth>
                    <InputLabel id="demo-simple-select-label">
                        Awesome Level
                    </InputLabel>
                    <Select
                        labelId="demo-simple-select-label"
                        id="demo-simple-select"
                        label="Awesome Level"
                        onChange={() => {}}
                    >
                        <MenuItem value={'Awesome'}>Awesome</MenuItem>
                        <MenuItem value={'Very Awesome'}>Very Awesome</MenuItem>
                        <MenuItem value={'Way Awesome'}>Way Awesome</MenuItem>
                    </Select>
                </FormControl>
                <FormControl fullWidth>
                    <TextField
                        id="standard-basic"
                        label="Standard"
                        variant="standard"
                    />
                </FormControl>
                <FormControlLabel control={<Switch />} label="Enabled" />
            </Stack>
        </Box>
    </Box>
);

export default AdminDashboard;
