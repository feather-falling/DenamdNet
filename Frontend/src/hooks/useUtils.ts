import { ref, watch, onMounted, onUnmounted, type Ref } from 'vue';

export function useDebounce<T>(value: Ref<T>, delay = 300): Ref<T> {
  const debounced = ref(value.value) as Ref<T>;
  
  let timeout: ReturnType<typeof setTimeout>;
  
  watch(value, (newValue) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      debounced.value = newValue;
    }, delay);
  });
  
  return debounced;
}

export function useKeyboardShortcut(
  key: string,
  callback: () => void,
  options: { ctrl?: boolean; meta?: boolean; shift?: boolean } = {}
) {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (options.ctrl && !e.ctrlKey) return;
    if (options.meta && !e.metaKey) return;
    if (options.shift && !e.shiftKey) return;
    if (e.key.toLowerCase() === key.toLowerCase()) {
      e.preventDefault();
      callback();
    }
  };
  
  onMounted(() => window.addEventListener('keydown', handleKeyDown));
  onUnmounted(() => window.removeEventListener('keydown', handleKeyDown));
}

export function useDisclosure(initial = false) {
  const isOpen = ref(initial);
  const open = () => { isOpen.value = true; };
  const close = () => { isOpen.value = false; };
  const toggle = () => { isOpen.value = !isOpen.value; };
  return { isOpen, open, close, toggle };
}
