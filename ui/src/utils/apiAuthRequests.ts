export interface AuthAccessRefreshToken {
    accessToken: string;
    refreshToken: string;
}

export interface StatusMessageResponse {
    message: string;
}

export interface AuthorizedRequestProps {
    accessToken: string;
    refreshToken: string;
    accessTokenRefreshCallback(newAccessToken: string): void;
}

export interface ApiRequestProps extends AuthorizedRequestProps {
    uri: string;
    method: string;
    requestBody?: any;
    contentType?: string;
}

export interface RefreshAccessTokenResponse {
    accessToken: string;
}

export interface ServerError {
    errorMessage: string;
}

export interface WhoAmIResponse {
    firstName: string;
    id: string;
    lastName: string;
    username: string;
}

export const isServerError = (content: any): content is ServerError => {
    return (content as ServerError)?.errorMessage !== undefined;
};

export const refreshAccessToken = async (
    refreshToken: string
): Promise<RefreshAccessTokenResponse | ServerError> => {
    try {
        const requestBody = {
            refreshToken,
        };

        const response = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // We're passing in the refresh token instead of the usual access token.
                Authorization: `Bearer ${refreshToken}`,
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) throw response.statusText;

        const result = await response.json();
        return result as RefreshAccessTokenResponse;
    } catch (error) {
        console.error('registration error:', error);
        return { errorMessage: (error as Error).message } as ServerError;
    }
};

export const apiRequest = async ({
    uri,
    method,
    accessToken,
    refreshToken,
    accessTokenRefreshCallback,
    requestBody,
    contentType = 'application/json',
}: ApiRequestProps): Promise<any | ServerError> => {
    try {
        if (!uri) {
            throw new Error('uri required');
        }
        if (!method) {
            throw new Error('method required');
        }
        if (!accessToken) {
            throw new Error('accessToken required');
        }

        const response = await fetch(uri, {
            method: method,
            headers: {
                'Content-Type': contentType,
                Authorization: `Bearer ${accessToken}`,
            },
            body: requestBody ? JSON.stringify(requestBody) : undefined,
        });

        const result = await response.json();

        // Access token expired likely, try to refresh it first and retry
        if (result?.body?.msg && result?.body?.msg.includes('token')) {
            console.log('access token likely expired, trying again');
            const newTokenResponse: RefreshAccessTokenResponse | ServerError =
                await refreshAccessToken(refreshToken);

            if (isServerError(newTokenResponse)) {
                console.error('apiRequest: unable to refresh access token');
                return {
                    errorMessage: 'unable to refresh access token',
                } as ServerError;
            }

            // update access token and return a new request promise
            console.log('access token refreshed, trying again');
            accessTokenRefreshCallback(newTokenResponse.accessToken);
            return apiRequest({
                uri,
                method,
                accessToken: newTokenResponse.accessToken,
                refreshToken,
                accessTokenRefreshCallback,
                requestBody,
                contentType,
            });
        }

        if (!response.ok) {
            throw new Error(result?.message ?? response.statusText);
        }

        return result;
    } catch (error) {
        console.error('login error:', error);
        return { errorMessage: (error as Error).message } as ServerError;
    }
};

// Login via the website API
export const login = async (
    username: string,
    password: string
): Promise<AuthAccessRefreshToken | ServerError> => {
    try {
        if (!username) {
            throw new Error('username required');
        }
        if (!password) {
            throw new Error('password required');
        }

        const requestBody = {
            username,
            password,
        };

        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result?.message ?? response.statusText);
        }

        return result as AuthAccessRefreshToken;
    } catch (error) {
        console.error('login error:', error);
        return { errorMessage: (error as Error).message } as ServerError;
    }
};

export const register = async (
    username: string,
    password: string,
    firstName: string,
    lastName: string
): Promise<StatusMessageResponse | ServerError> => {
    try {
        if (!username) {
            throw new Error('username required');
        }
        if (!password) {
            throw new Error('password required');
        }
        if (!firstName) {
            throw new Error('firstName required');
        }
        if (!lastName) {
            throw new Error('lastName required');
        }

        const requestBody = {
            username,
            password,
            firstName,
            lastName,
        };

        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) throw response.statusText;

        const result = await response.json();
        return result as StatusMessageResponse;
    } catch (error) {
        console.error('registration error:', error);
        return { errorMessage: (error as Error).message } as ServerError;
    }
};

export const logout = async ({
    accessToken,
    refreshToken,
    accessTokenRefreshCallback,
}: AuthorizedRequestProps): Promise<StatusMessageResponse | ServerError> => {
    const requestBody = {
        refreshToken: refreshToken,
    };

    const logoutResponse = await apiRequest({
        uri: '/api/auth/logout',
        method: 'POST',
        accessToken,
        refreshToken,
        accessTokenRefreshCallback,
        requestBody,
    });

    if (isServerError(logoutResponse)) {
        console.error('logout: unable to logout', logoutResponse);
        return {
            errorMessage: logoutResponse.errorMessage,
        } as ServerError;
    }

    return logoutResponse;
};

export const loginValid = async ({
    accessToken,
    refreshToken,
    accessTokenRefreshCallback,
}: AuthorizedRequestProps): Promise<boolean> => {
    const response = await apiRequest({
        uri: '/api/auth/valid',
        method: 'GET',
        accessToken,
        refreshToken,
        accessTokenRefreshCallback,
    });
    return isServerError(response) ? false : true;
};

export const whoAmI = async ({
    accessToken,
    refreshToken,
    accessTokenRefreshCallback,
}: AuthorizedRequestProps): Promise<WhoAmIResponse | ServerError> => {
    const response = await apiRequest({
        uri: '/api/auth/who-am-i',
        method: 'GET',
        accessToken,
        refreshToken,
        accessTokenRefreshCallback,
    });
    return response;
};
