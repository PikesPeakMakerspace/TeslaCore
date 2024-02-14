import { PaletteMode, Theme, createTheme, useMediaQuery } from '@mui/material';
import React, {
    ReactNode,
    useCallback,
    useContext,
    useEffect,
    useRef,
    useState,
} from 'react';
import {
    loadFromLocalStorage,
    saveToLocalStorage,
} from '../../utils/localStorage';
import {
    ServerError,
    isServerError,
    login,
    logout,
    refreshAccessToken,
} from '../../utils/apiAuthRequests';

const REFRESH_INTERVAL_MILLISECONDS = 1800000; // 30 minutes

export interface UseAppContext {
    theme?: Theme;
    toggleThemePaletteMode: () => void;
    appLogin: (username: string, password: string) => void;
    appLogout: () => void;
    loggedIn: boolean;
    loading: boolean;
}
export interface AppContextProviderProps {
    children: ReactNode;
}

const AppContext = React.createContext<UseAppContext>({
    toggleThemePaletteMode: () => {},
    appLogin: () => {},
    appLogout: () => {},
    loggedIn: false,
    loading: false,
});

export function AppContextProvider(props: AppContextProviderProps) {
    const systemPaletteMode = useMediaQuery('(prefers-color-scheme: dark)')
        ? 'dark'
        : 'light';
    const [themePaletteMode, setThemePaletteMode] =
        React.useState<PaletteMode>(systemPaletteMode);
    const [loggedIn, setLoggedIn] = useState(false);
    const [loading, setLoading] = useState(true);

    const accessToken = useRef('');
    const refreshToken = useRef('');
    const lastTokenRefresh = useRef(0);

    const theme = createTheme({
        palette: {
            mode: themePaletteMode,
            primary: {
                main: '#3d6774',
            },
            secondary: {
                main: '#7a3872',
            },
            error: {
                main: '#c33c25',
            },
            warning: {
                main: '#bc6e23',
            },
            info: {
                main: '#dd6585',
            },
            success: {
                main: '#546831',
            },
        },
        components: {
            MuiAppBar: {
                defaultProps: {
                    enableColorOnDark: true,
                },
            },
        },
    });

    const toggleThemePaletteMode = useCallback(() => {
        const savedThemePaletteMode = loadFromLocalStorage('themePaletteMode');
        const newPaletteMode =
            savedThemePaletteMode === 'dark' ? 'light' : 'dark';
        saveToLocalStorage('themePaletteMode', newPaletteMode);
        setThemePaletteMode(newPaletteMode);
    }, []);

    // Keep the access token fresh for continued website access.
    const updateAccessToken = useCallback(async (): Promise<void> => {
        // not logged in yet, no need to proceed
        if (!refreshToken.current) {
            console.log('no refresh token to refresh with yet...');
            setLoading(false);
            setLoggedIn(false);
            return;
        }

        // not time to refresh token yet
        if (
            Date.now() - lastTokenRefresh.current <
                REFRESH_INTERVAL_MILLISECONDS &&
            loggedIn === true
        ) {
            return;
        }

        const newAccessTokenResponse = await refreshAccessToken(
            refreshToken.current
        );

        if (isServerError(newAccessTokenResponse)) {
            console.error(
                'error refreshing token, time for new login/refresh token',
                newAccessTokenResponse.errorMessage
            );
            setLoggedIn(false);
            accessToken.current = '';
            refreshToken.current = '';
            lastTokenRefresh.current = 0;
            return;
        }

        accessToken.current = newAccessTokenResponse?.accessToken ?? '';
        lastTokenRefresh.current = Date.now();
        setLoading(false);
        setLoggedIn(true);
    }, [loggedIn]);

    const appLogin = async (
        username: string,
        password: string
    ): Promise<void | ServerError> => {
        setLoggedIn(false);

        const loginResponse = await login(username, password);
        if (isServerError(loginResponse)) {
            return loginResponse as ServerError;
        }

        accessToken.current = loginResponse.accessToken;
        refreshToken.current = loginResponse.refreshToken;
        lastTokenRefresh.current = Date.now();
        saveToLocalStorage('refreshToken', loginResponse.refreshToken);
        setLoggedIn(true);
    };

    const appLogout = async (): Promise<void | ServerError> => {
        const logoutResponse = await logout(
            accessToken.current,
            refreshToken.current,
            (newAccessToken) => {
                accessToken.current = newAccessToken;
            }
        );

        accessToken.current = '';
        refreshToken.current = '';
        saveToLocalStorage('refreshToken', '');
        setLoggedIn(false);

        if (isServerError(logoutResponse)) {
            return logoutResponse as ServerError;
        }

        return;
    };

    // on load, set dark mode to stored dark mode, then system pref, then dark default
    useEffect(() => {
        const savedThemePaletteMode = loadFromLocalStorage('themePaletteMode');
        const themePaletteMode: PaletteMode = (savedThemePaletteMode ??
            systemPaletteMode) as PaletteMode;
        if (!savedThemePaletteMode) {
            saveToLocalStorage('themePaletteMode', themePaletteMode);
        }
        setThemePaletteMode(themePaletteMode);
    }, [systemPaletteMode]);

    // get locally stored auth token data on load
    useEffect(() => {
        accessToken.current = '';
        refreshToken.current = loadFromLocalStorage('refreshToken') ?? '';

        if (!refreshToken.current) {
            setLoggedIn(false);
            setLoading(false);
            return;
        }

        const refreshInterval = setInterval(() => {
            updateAccessToken();
        }, 60000);

        // update the token right away if applicable
        updateAccessToken();

        return () => {
            clearInterval(refreshInterval);
        };
    }, [updateAccessToken]);

    return (
        <AppContext.Provider
            value={{
                theme,
                toggleThemePaletteMode,
                appLogin,
                appLogout,
                loggedIn,
                loading,
            }}
        >
            {props.children}
        </AppContext.Provider>
    );
}

export const useAppContext = () => useContext(AppContext);
