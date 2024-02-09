import React, { useCallback, useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import MenuIcon from '@mui/icons-material/Menu';
import Container from '@mui/material/Container';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import MenuItem from '@mui/material/MenuItem';
import ElectricalServicesIcon from '@mui/icons-material/ElectricalServices';
import { Link, matchPath, useLocation } from 'react-router-dom';
import { useTheme } from '@mui/material/styles';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import { useAppContext } from '../App/AppContext';

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

// thanks: https://stackoverflow.com/a/7616484/1279000
const profileImageHashUrl = (username: string): string => {
    let hash = 0,
        i,
        chr;
    for (i = 0; i < username.length; i++) {
        chr = username.charCodeAt(i);
        hash = (hash << 5) - hash + chr;
        hash |= 0; // Convert to 32bit integer
    }

    const profileUrl = `https://gravatar.com/avatar/${hash}?d=retro&f=y`;
    return profileUrl;
};

function TopNav() {
    const [anchorElNav, setAnchorElNav] = useState<null | HTMLElement>(null);
    const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);

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
    const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorElUser(event.currentTarget);
    };

    const handleCloseNavMenu = () => {
        setAnchorElNav(null);
    };

    const handleCloseUserMenu = () => {
        setAnchorElUser(null);
    };

    const handleLogoutClick = useCallback(async () => {
        appContext.appLogout();
    }, [appContext]);

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

                    <Box sx={{ flexGrow: 0 }}>
                        <Tooltip title="Open settings">
                            <IconButton
                                onClick={handleOpenUserMenu}
                                sx={{ p: 0 }}
                            >
                                <Avatar
                                    alt="Remy Sharp"
                                    src={profileImageHashUrl('bob@example.com')}
                                />
                            </IconButton>
                        </Tooltip>
                        <Menu
                            sx={{ mt: '45px' }}
                            id="menu-appbar"
                            anchorEl={anchorElUser}
                            anchorOrigin={{
                                vertical: 'top',
                                horizontal: 'right',
                            }}
                            keepMounted
                            transformOrigin={{
                                vertical: 'top',
                                horizontal: 'right',
                            }}
                            open={Boolean(anchorElUser)}
                            onClose={handleCloseUserMenu}
                        >
                            <MenuItem
                                key="Logout"
                                component={Link}
                                to="/logout"
                                onClick={handleLogoutClick}
                            >
                                <Typography textAlign="center">
                                    Logout
                                </Typography>
                            </MenuItem>
                        </Menu>
                    </Box>
                </Toolbar>
            </Container>
        </AppBar>
    );
}
export default TopNav;
