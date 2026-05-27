'use client';

import { createContext, useCallback, useContext, useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, XCircle, Info, AlertTriangle, X } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration: number;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  success: (title: string, message?: string) => void;
  error: (title: string, message?: string) => void;
  info: (title: string, message?: string) => void;
  warning: (title: string, message?: string) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}

const ICONS: Record<ToastType, LucideIcon> = {
  success: CheckCircle2,
  error: XCircle,
  info: Info,
  warning: AlertTriangle,
};

const COLORS: Record<ToastType, { border: string; icon: string; bg: string }> = {
  success: { border: 'border-l-emerald-500', icon: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  error: { border: 'border-l-red-500', icon: 'text-red-400', bg: 'bg-red-500/10' },
  info: { border: 'border-l-indigo-500', icon: 'text-indigo-400', bg: 'bg-indigo-500/10' },
  warning: { border: 'border-l-amber-500', icon: 'text-amber-400', bg: 'bg-amber-500/10' },
};

export function ToastProvider({ children }: { children?: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).slice(2, 10);
    setToasts((t) => [...t, { ...toast, id }]);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((t) => t.filter((toast) => toast.id !== id));
  }, []);

  // Backwards-compatible: accept single string as title
  const success = useCallback(
    (title: string, message?: string) => addToast({ type: 'success', title, message, duration: 4000 }),
    [addToast]
  );
  const error = useCallback(
    (title: string, message?: string) => addToast({ type: 'error', title, message, duration: 8000 }),
    [addToast]
  );
  const info = useCallback(
    (title: string, message?: string) => addToast({ type: 'info', title, message, duration: 4000 }),
    [addToast]
  );
  const warning = useCallback(
    (title: string, message?: string) => addToast({ type: 'warning', title, message, duration: 6000 }),
    [addToast]
  );

  // Expose globally
  useEffect(() => {
    (window as unknown as Record<string, unknown>).toast = {
      toasts,
      addToast,
      removeToast,
      success,
      error,
      info,
      warning,
    };
  }, [toasts, addToast, removeToast, success, error, info, warning]);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, success, error, info, warning }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-3 pointer-events-none" aria-live="polite">
        <AnimatePresence mode="popLayout">
          {toasts.slice(-3).map((toast) => (
            <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onClose }: { toast: Toast; onClose: () => void }) {
  const onCloseRef = useRef(onClose);
  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);
  useEffect(() => {
    const timer = setTimeout(() => onCloseRef.current(), toast.duration);
    return () => clearTimeout(timer);
  }, [toast.duration]);

  const Icon = ICONS[toast.type];
  const colors = COLORS[toast.type];

  return (
    <motion.div
      initial={{ opacity: 0, x: 50, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 50, scale: 0.9, transition: { duration: 0.2 } }}
      className={`relative w-80 pointer-events-auto border-l-4 ${colors.border} ${colors.bg} p-4 overflow-hidden rounded-lg`}
      style={{
        backgroundColor: 'var(--color-bg-surface)',
        borderRight: '1px solid var(--color-border-default)',
        borderTop: '1px solid var(--color-border-default)',
        borderBottom: '1px solid var(--color-border-default)',
      }}
      role="status"
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${colors.icon}`} />
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-sm" style={{ color: 'var(--color-text-primary)' }}>{toast.title}</div>
          {toast.message && (
            <div className="text-xs mt-1" style={{ color: 'var(--color-text-secondary)' }}>{toast.message}</div>
          )}
        </div>
        <button
          onClick={onClose}
          className="shrink-0 transition-colors"
          style={{ color: 'var(--color-text-tertiary)' }}
          aria-label="Dismiss notification"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      <motion.div
        initial={{ scaleX: 1 }}
        animate={{ scaleX: 0 }}
        transition={{ duration: toast.duration / 1000, ease: 'linear' }}
        style={{ transformOrigin: 'left' }}
        className={`absolute bottom-0 left-0 h-0.5 w-full ${toast.type === 'success' ? 'bg-emerald-500' : toast.type === 'error' ? 'bg-red-500' : toast.type === 'info' ? 'bg-indigo-500' : 'bg-amber-500'}`}
      />
    </motion.div>
  );
}
