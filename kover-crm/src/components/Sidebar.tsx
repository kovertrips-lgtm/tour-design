'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Users, Trello, Calendar, Settings, PieChart, Mountain } from 'lucide-react';
import styles from './Sidebar.module.css';
import { clsx } from 'clsx';

const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Deals', href: '/deals', icon: Trello },
    { name: 'Contacts', href: '/contacts', icon: Users },
    { name: 'Tours', href: '/tours', icon: Mountain },
    { name: 'Calendar', href: '/calendar', icon: Calendar },
    { name: 'Analytics', href: '/analytics', icon: PieChart },
    { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className={styles.sidebar}>
            <div className={styles.logo}>
                <div className={styles.logoIcon}>
                    <Mountain size={18} color="white" />
                </div>
                <span>Antigravity</span>
            </div>

            <nav className={styles.nav}>
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={clsx(styles.navItem, isActive && styles.active)}
                        >
                            <Icon size={18} />
                            <span>{item.name}</span>
                        </Link>
                    );
                })}
            </nav>

            <div className={styles.userProfile}>
                <div className={styles.avatar}>A</div>
                <div style={{ fontSize: '14px' }}>
                    <div style={{ fontWeight: 600 }}>Alex</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Admin</div>
                </div>
            </div>
        </aside>
    );
}
