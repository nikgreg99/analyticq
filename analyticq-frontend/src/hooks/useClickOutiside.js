import { useEffect } from "react";
/**
 * A custom hook that detects clicks outside specified elements and triggers a callback.
 *
 * @param {React.RefObject[]} refs - An array of React refs to monitor for outside clicks
 * @param {Function} onClickOutside - Callback function to execute when a click occurs outside the referenced elements
 *
 * @example
 * const ref1 = useRef(null);
 * const ref2 = useRef(null);
 * useClickOutside([ref1, ref2], () => console.log('Clicked outside'));
 */
export function useClickOutside(refs, onClickOutside) {
  useEffect(() => {
    const handleClickOutside = (event) => {
      const clickedInside = refs.some(
        (ref) => ref.current && ref.current.contains(event.target),
      );

      if (!clickedInside) {
        onClickOutside();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [refs, onClickOutside]);
}
