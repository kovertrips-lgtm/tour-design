'use client';

import React, { useState } from 'react';
import Card from '@/components/Card';
import { MoreHorizontal, Plus, Calendar as CalendarIcon, DollarSign } from 'lucide-react';

const COLUMNS = [
    { id: 'new', title: 'New Request', color: '#3b82f6' },
    { id: 'contacted', title: 'Contacted', color: '#8b5cf6' },
    { id: 'deposit', title: 'Deposit Paid', color: '#f59e0b' },
    { id: 'paid', title: 'Fully Paid', color: '#10b981' },
];

const INITIAL_DEALS = [
    { id: 1, title: 'Alps Tour - Family Smith', name: 'John Smith', amount: 2400, date: 'Jan 24', status: 'new' },
    { id: 2, title: 'Skiing Weekend', name: 'Maria Garcia', amount: 850, date: 'Jan 23', status: 'new' },
    { id: 3, title: 'Hiking Group A', name: 'Alex K.', amount: 3200, date: 'Jan 22', status: 'contacted' },
    { id: 4, title: 'Couple Retreat', name: 'Sarah & Tom', amount: 1200, date: 'Jan 20', status: 'deposit' },
    { id: 5, title: 'Solo Adventure', name: 'Mike Ross', amount: 600, date: 'Jan 15', status: 'paid' },
];

export default function DealsPage() {
    const [deals, setDeals] = useState(INITIAL_DEALS);

    return (
        <div style={{ height: 'calc(100vh - 80px)', display: 'flex', flexDirection: 'column' }}>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <div>
                    <h1 style={{ fontSize: '32px', fontWeight: 700 }}>Deals Pipeline</h1>
                </div>
                <button style={{
                    background: 'var(--primary)',
                    border: 'none',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    color: 'white',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    cursor: 'pointer'
                }}>
                    <Plus size={18} />
                    Add Deal
                </button>
            </header>

            <div style={{
                display: 'flex',
                gap: '16px',
                overflowX: 'auto',
                paddingBottom: '20px',
                flex: 1
            }}>
                {COLUMNS.map(col => (
                    <div key={col.id} style={{
                        minWidth: '300px',
                        background: 'rgba(255,255,255,0.02)',
                        borderRadius: '16px',
                        padding: '16px',
                        display: 'flex',
                        flexDirection: 'column'
                    }}>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '16px',
                            paddingBottom: '12px',
                            borderBottom: `2px solid ${col.color}`
                        }}>
                            <span style={{ fontWeight: 600, fontSize: '14px' }}>{col.title}</span>
                            <span style={{
                                background: 'rgba(255,255,255,0.1)',
                                padding: '2px 8px',
                                borderRadius: '12px',
                                fontSize: '12px'
                            }}>
                                {deals.filter(d => d.status === col.id).length}
                            </span>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1, overflowY: 'auto' }}>
                            {deals.filter(d => d.status === col.id).map(deal => (
                                <div key={deal.id} style={{
                                    background: 'var(--bg-card)',
                                    padding: '16px',
                                    borderRadius: '12px',
                                    border: '1px solid var(--border)',
                                    cursor: 'grab',
                                    boxShadow: 'var(--shadow-sm)'
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>#{deal.id}</span>
                                        <MoreHorizontal size={14} color="var(--text-muted)" />
                                    </div>
                                    <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '4px' }}>{deal.title}</h4>
                                    <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '12px' }}>{deal.name}</p>

                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto' }}>
                                        <div style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '4px',
                                            fontSize: '12px',
                                            background: 'rgba(59, 130, 246, 0.1)',
                                            padding: '4px 8px',
                                            borderRadius: '6px',
                                            color: 'var(--primary)'
                                        }}>
                                            <DollarSign size={12} />
                                            {deal.amount}
                                        </div>
                                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                            <CalendarIcon size={12} />
                                            {deal.date}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
