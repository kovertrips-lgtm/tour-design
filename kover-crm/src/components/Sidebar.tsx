'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Trello,
    Users,
    Settings,
    Inbox,
    PieChart
} from 'lucide-react';
import styles from './Sidebar.module.css';
import { clsx } from 'clsx';

const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Leads', href: '/deals', icon: Trello },
    { name: 'Inbox', href: '/inbox', icon: Inbox },
    { name: 'Contacts', href: '/contacts', icon: Users },
    { name: 'Analytics', href: '/analytics', icon: PieChart },
    { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className={styles.sidebar}>
            <div className={styles.logo}>
                <div style={{ width: 24, height: 24, background: '#4c8bf5', borderRadius: '4px' }}></div>
            </div>

            {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
                return (
                    <Link
                        key={item.href}
                        href={item.href}
                        className={clsx(styles.navItem, isActive && styles.active)}
                        data-tooltip={item.name}
                    >
                        <Icon size={18} strokeWidth={2} />
                    </Link>
                );
            })}

            <div className={styles.user}>
                <div className={styles.navItem}>
                    <div style={{ width: 24, height: 24, background: '#6ccb5f', borderRadius: '50%', fontSize: '10px', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>A</div>
                </div>
            </div>
        </aside>
    );
}
