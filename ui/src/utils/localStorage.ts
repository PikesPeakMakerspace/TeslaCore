export const saveToLocalStorage = (key: string, value: string) => {
    localStorage[key] = value;
};

export const loadFromLocalStorage = (key: string): string | null => {
    return localStorage[key] ?? null;
};
