import React, { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import MenuIcon from '@mui/icons-material/Menu';
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import MenuItem from '@mui/material/MenuItem';
import ElectricalServicesIcon from '@mui/icons-material/ElectricalServices';
import { Link, matchPath, useLocation } from 'react-router-dom';
import { useTheme } from '@mui/material/styles';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import { useAppContext } from '../App/AppContext';
import UserDropdownMenu from './UserDropdownMenu';

interface PageTitleUri {
    title: string;
    uri: string[];
}

const pages: PageTitleUri[] = [
    { title: 'Users', uri: ['/users', '/users/:id'] },
    { title: 'Access Cards', uri: ['/accessCards', '/accessCards/:id'] },
    { title: 'Devices', uri: ['/devices', '/devices/:id'] },
    { title: 'Access Nodes', uri: ['/accessNodes', 'accessNodes/:id'] },
    { title: 'Reports', uri: ['/reports', '/reports/:id'] },
];

function TopNav() {
    const [anchorElNav, setAnchorElNav] = useState<null | HTMLElement>(null);

    const theme = useTheme();
    const appContext = useAppContext();

    const useRouteMatch = (patterns: readonly string[]) => {
        const { pathname } = useLocation();

        for (let i = 0; i < patterns.length; i += 1) {
            const pattern = patterns[i];
            const possibleMatch = matchPath(pattern, pathname);
            if (possibleMatch !== null) {
                return possibleMatch;
            }
        }

        return null;
    };

    const handleOpenNavMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorElNav(event.currentTarget);
    };

    const handleCloseNavMenu = () => {
        setAnchorElNav(null);
    };

    // get the current route so its active menu item can be highlighted
    const routeMatch = useRouteMatch(
        pages
            .map((page) => {
                return page.uri;
            })
            .flat(1)
    );
    const currentTab = routeMatch?.pattern?.path;

    return (
        <AppBar position="static">
            <Container maxWidth="lg">
                <Toolbar disableGutters>
                    <ElectricalServicesIcon
                        sx={{ display: { xs: 'none', md: 'flex' }, mr: 1 }}
                    />
                    <Typography
                        variant="h6"
                        noWrap
                        component={Link}
                        to="/"
                        sx={{
                            mr: 2,
                            display: { xs: 'none', md: 'flex' },
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            letterSpacing: '.3rem',
                            color: 'inherit',
                            textDecoration: 'none',
                        }}
                    >
                        TESLA
                    </Typography>

                    <Box
                        sx={{
                            flexGrow: 1,
                            display: { xs: 'flex', md: 'none' },
                        }}
                    >
                        <IconButton
                            size="large"
                            aria-label="account of current user"
                            aria-controls="menu-appbar"
                            aria-haspopup="true"
                            onClick={handleOpenNavMenu}
                            color="inherit"
                        >
                            <MenuIcon />
                        </IconButton>
                        <Menu
                            id="menu-appbar"
                            anchorEl={anchorElNav}
                            anchorOrigin={{
                                vertical: 'bottom',
                                horizontal: 'left',
                            }}
                            keepMounted
                            transformOrigin={{
                                vertical: 'top',
                                horizontal: 'left',
                            }}
                            open={Boolean(anchorElNav)}
                            onClose={handleCloseNavMenu}
                            sx={{
                                display: { xs: 'block', md: 'none' },
                            }}
                        >
                            {pages.map((page) => (
                                <MenuItem
                                    key={page.title}
                                    onClick={handleCloseNavMenu}
                                    component={Link}
                                    to={page.uri[0]}
                                >
                                    <Typography textAlign="center">
                                        {page.title}
                                    </Typography>
                                </MenuItem>
                            ))}
                        </Menu>
                    </Box>
                    <ElectricalServicesIcon
                        sx={{ display: { xs: 'flex', md: 'none' }, mr: 1 }}
                    />
                    <Typography
                        variant="h5"
                        noWrap
                        component={Link}
                        to={'/'}
                        sx={{
                            mr: 2,
                            display: { xs: 'flex', md: 'none' },
                            flexGrow: 1,
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            letterSpacing: '.3rem',
                            color: 'inherit',
                            textDecoration: 'none',
                        }}
                    >
                        TESLA
                    </Typography>
                    <Box
                        sx={{
                            flexGrow: 1,
                            display: { xs: 'none', md: 'flex' },
                        }}
                    >
                        {pages.map((page) => (
                            <Button
                                key={page.title}
                                sx={{
                                    my: 2,
                                    px: 2,
                                    display: 'block',
                                    color: page.uri.includes(currentTab ?? '')
                                        ? 'white'
                                        : 'rgba(255, 255, 255, 0.6)',
                                }}
                                component={Link}
                                to={page.uri[0]}
                            >
                                {page.title}
                            </Button>
                        ))}
                    </Box>

                    <Box sx={{ flexGrow: 0, mr: 1 }}>
                        <IconButton
                            sx={{ ml: 1 }}
                            onClick={appContext.toggleThemePaletteMode}
                            color="inherit"
                        >
                            {theme.palette.mode === 'dark' ? (
                                <DarkModeIcon />
                            ) : (
                                <LightModeIcon />
                            )}
                        </IconButton>
                    </Box>

                    <UserDropdownMenu />
                </Toolbar>
            </Container>
        </AppBar>
    );
}
export default TopNav;
