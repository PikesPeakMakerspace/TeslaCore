import React, { useCallback, useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import Avatar from '@mui/material/Avatar';
import Tooltip from '@mui/material/Tooltip';
import MenuItem from '@mui/material/MenuItem';
import { Link } from 'react-router-dom';
import { useAppContext } from '../App/AppContext';
import { isServerError, whoAmI } from '../../utils/apiAuthRequests';

export interface UserDropdownProfile {
    firstName: string;
    lastName: string;
    imageUrl: string;
}

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

function UserDropdownMenu() {
    const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);
    const [profile, setProfile] = useState<UserDropdownProfile>({
        firstName: 'Loading...',
        lastName: '',
        imageUrl:
            'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y',
    });

    const appContext = useAppContext();

    const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorElUser(event.currentTarget);
    };

    const handleCloseUserMenu = () => {
        setAnchorElUser(null);
    };

    const handleLogoutClick = useCallback(async () => {
        appContext.appLogout();
    }, [appContext]);

    useEffect(() => {
        const getUserInfo = async () => {
            if (appContext.loggedIn === false) {
                return;
            }

            const profile = await appContext.appApiRequest({
                requestFunction: whoAmI,
            });
            if (isServerError(profile) || !profile) {
                return;
            }

            const imageUrl = await profileImageHashUrl(profile.username ?? '');
            setProfile({
                firstName: profile.firstName,
                lastName: profile.lastName,
                imageUrl,
            });
        };
        getUserInfo();
    }, [appContext, appContext.loggedIn]);

    return (
        <Box sx={{ flexGrow: 0 }}>
            <Tooltip title="Open settings">
                <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                    <Avatar
                        alt={`${profile.firstName} ${profile.lastName}`}
                        src={profile.imageUrl}
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
                    <Typography textAlign="center">Logout</Typography>
                </MenuItem>
            </Menu>
        </Box>
    );
}
export default UserDropdownMenu;
