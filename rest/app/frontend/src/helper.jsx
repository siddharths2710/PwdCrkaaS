import { useEffect, useRef, useState } from "react";

export function useTimedState(initialState, timeout) {
    const [state, setState] = useState(initialState);
    const timerRef = useRef(undefined);

    const setValue = (value) => {
        setState(value);
        timerRef.current = setTimeout(() => {
            setState(!value);
            timerRef.current = undefined;
        }, timeout);
    }

    useEffect(() => {
        return () => {
            if (timerRef.current) {
                clearTimeout(timerRef.current);
            }
        }
    }, []);

    return [state, setValue];
}
