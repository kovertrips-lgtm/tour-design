import React from 'react';
import styles from './Card.module.css';

interface CardProps {
    title?: string;
    icon?: React.ReactNode;
    children: React.ReactNode;
    className?: string;
}

export default function Card({ title, icon, children, className }: CardProps) {
    return (
        <div className={`${styles.card} ${className || ''}`}>
            {(title || icon) && (
                <div className={styles.header}>
                    {title && <h3 className={styles.title}>{title}</h3>}
                    {icon && <div className={styles.icon}>{icon}</div>}
                </div>
            )}
            <div className={styles.content}>{children}</div>
        </div>
    );
}
