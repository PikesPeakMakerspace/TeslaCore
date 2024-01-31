import { PaletteMode, Theme, createTheme, useMediaQuery } from '@mui/material';
import React, { ReactNode, useContext, useEffect } from 'react';
import {
    loadFromLocalStorage,
    saveToLocalStorage,
} from '../../utils/localStorage';

export interface UseAppContext {
    theme?: Theme;
    toggleThemePaletteMode?: () => void;
}

export interface AppContextProviderProps {
    children: ReactNode;
}

const AppContext = React.createContext<UseAppContext>({});

export function AppContextProvider(props: AppContextProviderProps) {
    const systemPaletteMode = useMediaQuery('(prefers-color-scheme: dark)')
        ? 'dark'
        : 'light';
    const [themePaletteMode, setThemePaletteMode] =
        React.useState<PaletteMode>(systemPaletteMode);

    const theme = createTheme({
        palette: {
            mode: themePaletteMode,
            primary: {
                main: '#685FC7',
            },
            secondary: {
                main: '#436ED1',
            },
            error: {
                main: '#911350',
            },
            warning: {
                main: '#757523',
            },
            info: {
                main: '#8B548E',
            },
            success: {
                main: '#00806A',
            },
        },
    });

    const toggleThemePaletteMode = () => {
        console.log('toggle');
        const curIsDarkMode =
            loadFromLocalStorage('isDarkMode') === 'true' ? true : false;
        saveToLocalStorage('isDarkMode', (!curIsDarkMode).toString());
        setThemePaletteMode(curIsDarkMode === true ? 'light' : 'dark');
    };

    // on load, set dark mode to stored dark mode, then system pref, then dark default
    // TODO: Just save 'light' or 'dark' to simplify
    useEffect(() => {
        const savedThemePaletteMode = loadFromLocalStorage('themePaletteMode');
        const themePaletteMode: PaletteMode = (savedThemePaletteMode ??
            systemPaletteMode) as PaletteMode;
        console.log(themePaletteMode);
        if (!savedThemePaletteMode) {
            saveToLocalStorage('themePaletteMode', themePaletteMode);
        }
        setThemePaletteMode(themePaletteMode);
    }, [systemPaletteMode]);

    return (
        <AppContext.Provider
            value={{
                theme,
                toggleThemePaletteMode,
            }}
        >
            {props.children}
        </AppContext.Provider>
    );
}

export const useAppContext = () => useContext(AppContext);
