'use client';

import React from 'react';
import { Mail, Phone, Search, Filter } from 'lucide-react';

const CONTACTS = [
    { id: 1, name: 'John Smith', email: 'john@example.com', phone: '+1 234 567 890', tags: ['VIP', 'Alps'] },
    { id: 2, name: 'Maria Garcia', email: 'maria@example.com', phone: '+34 123 456 789', tags: ['New'] },
    { id: 3, name: 'Alex K', email: 'alex@kover.travel', phone: '+420 123 456 789', tags: ['Team'] },
    { id: 4, name: 'Sarah Connor', email: 'sarah@skynet.com', phone: '+1 987 654 321', tags: ['Lead'] },
    { id: 5, name: 'Mike Ross', email: 'mike@pearman.com', phone: '+1 555 0199', tags: ['Alps'] },
];

export default function ContactsPage() {
    return (
        <div>
            <header style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1 style={{ fontSize: '32px', fontWeight: 700 }}>Contacts</h1>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <div style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border)',
                        padding: '10px 16px',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        width: '300px'
                    }}>
                        <Search size={16} color="var(--text-muted)" />
                        <input
                            type="text"
                            placeholder="Search contacts..."
                            style={{
                                background: 'transparent',
                                border: 'none',
                                color: 'white',
                                outline: 'none',
                                width: '100%'
                            }}
                        />
                    </div>
                    <button style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border)',
                        padding: '10px',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        color: 'var(--text-muted)'
                    }}>
                        <Filter size={20} />
                    </button>
                </div>
            </header>

            <div style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: '16px',
                overflow: 'hidden'
            }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border)' }}>
                            <th style={{ padding: '16px 24px', textAlign: 'left', fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Name</th>
                            <th style={{ padding: '16px 24px', textAlign: 'left', fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Contact Info</th>
                            <th style={{ padding: '16px 24px', textAlign: 'left', fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Tags</th>
                            <th style={{ padding: '16px 24px', textAlign: 'left', fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {CONTACTS.map((contact) => (
                            <tr key={contact.id} style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-main)' }}>
                                <td style={{ padding: '16px 24px' }}>
                                    <div style={{ fontWeight: 500 }}>{contact.name}</div>
                                </td>
                                <td style={{ padding: '16px 24px' }}>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '13px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)' }}>
                                            <Mail size={12} /> {contact.email}
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)' }}>
                                            <Phone size={12} /> {contact.phone}
                                        </div>
                                    </div>
                                </td>
                                <td style={{ padding: '16px 24px' }}>
                                    <div style={{ display: 'flex', gap: '6px' }}>
                                        {contact.tags.map(tag => (
                                            <span key={tag} style={{
                                                fontSize: '11px',
                                                padding: '2px 8px',
                                                borderRadius: '10px',
                                                background: 'rgba(255, 255, 255, 0.1)',
                                                border: '1px solid rgba(255,255,255,0.1)'
                                            }}>
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </td>
                                <td style={{ padding: '16px 24px' }}>
                                    <button style={{
                                        color: 'var(--primary)',
                                        background: 'transparent',
                                        border: 'none',
                                        cursor: 'pointer',
                                        fontSize: '13px',
                                        fontWeight: 500
                                    }}>
                                        View
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
