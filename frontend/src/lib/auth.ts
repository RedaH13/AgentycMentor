const TOKEN_KEY = "mas_token";
const ROLE_KEY = "mas_role";

export const setAuthData = (token: string, role: string) => {
    if (typeof window !== "undefined") {
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(ROLE_KEY, role);
    }
};

export const getToken = (): string | null => {
    if (typeof window !== "undefined") {
        return localStorage.getItem(TOKEN_KEY);
    }
    return null;
};

export const getRole = (): string | null => {
    if (typeof window !== "undefined") {
        return localStorage.getItem(ROLE_KEY);
    }
    return null;
};

export const isAuthenticated = (): boolean => {
    return !!getToken();
};

export const logout = () => {
    if (typeof window !== "undefined") {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(ROLE_KEY);
        window.location.href = "/login"; // redirect to login
    }
};