'use client';
import React from 'react';

export default function PlaceholderPage({ title }: { title: string }) {
    return (
        <div style={{ padding: '40px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#8c9fa6' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🚧</div>
            <h1 style={{ fontSize: '24px', fontWeight: 600, color: '#313942', marginBottom: '8px' }}>{title}</h1>
            <p>This module is under development.</p>
        </div>
    );
}
