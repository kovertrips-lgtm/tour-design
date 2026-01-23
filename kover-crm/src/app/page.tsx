'use client';

import React from 'react';
import Card from '@/components/Card';
import { DollarSign, Users, TrendingUp, Activity } from 'lucide-react';

export default function Dashboard() {
  return (
    <div>
      <header style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 700, marginBottom: '8px' }}>Dashboard</h1>
        <p style={{ color: 'var(--text-muted)' }}>Overview of your tour operations</p>
      </header>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '24px',
        marginBottom: '40px'
      }}>
        <Card title="Total Revenue" icon={<DollarSign size={20} color="var(--success)" />}>
          <div style={{ fontSize: '32px', fontWeight: 700 }}>€124,500</div>
          <div style={{ fontSize: '14px', color: 'var(--success)', marginTop: '8px' }}>+12% from last month</div>
        </Card>

        <Card title="Active Deals" icon={<TrendingUp size={20} color="var(--primary)" />}>
          <div style={{ fontSize: '32px', fontWeight: 700 }}>42</div>
          <div style={{ fontSize: '14px', color: 'var(--text-muted)', marginTop: '8px' }}>18 closing this week</div>
        </Card>

        <Card title="Total Clients" icon={<Users size={20} color="var(--secondary)" />}>
          <div style={{ fontSize: '32px', fontWeight: 700 }}>1,204</div>
          <div style={{ fontSize: '14px', color: 'var(--success)', marginTop: '8px' }}>+8 new today</div>
        </Card>

        <Card title="Conversion Rate" icon={<Activity size={20} color="var(--warning)" />}>
          <div style={{ fontSize: '32px', fontWeight: 700 }}>3.8%</div>
          <div style={{ fontSize: '14px', color: 'var(--text-muted)', marginTop: '8px' }}>Target: 5.0%</div>
        </Card>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <Card title="Recent Bookings">
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '16px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)', textAlign: 'left' }}>
                <th style={{ padding: '12px 0', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase' }}>Client</th>
                <th style={{ padding: '12px 0', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase' }}>Tour</th>
                <th style={{ padding: '12px 0', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase' }}>Amount</th>
                <th style={{ padding: '12px 0', color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'Polina Petrova', tour: 'Alps Weekend', amount: '€450', status: 'Paid' },
                { name: 'Ivan Ivanov', tour: 'Skiing Masterclass', amount: '€1,200', status: 'Deposit' },
                { name: 'Elena Smirnova', tour: 'Hiking Adventure', amount: '€890', status: 'New' },
              ].map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '16px 0', fontSize: '14px' }}>{row.name}</td>
                  <td style={{ padding: '16px 0', fontSize: '14px', color: 'var(--text-muted)' }}>{row.tour}</td>
                  <td style={{ padding: '16px 0', fontSize: '14px', fontWeight: 600 }}>{row.amount}</td>
                  <td style={{ padding: '16px 0' }}>
                    <span style={{
                      fontSize: '12px',
                      padding: '4px 8px',
                      borderRadius: '12px',
                      background: row.status === 'Paid' ? 'rgba(16, 185, 129, 0.2)' : row.status === 'Deposit' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                      color: row.status === 'Paid' ? 'var(--success)' : row.status === 'Deposit' ? 'var(--primary)' : 'var(--text-muted)'
                    }}>
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        <Card title="Tasks">
          <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {[
              { text: 'Call Alex about refund', due: 'Today' },
              { text: 'Update photos for Alps tour', due: 'Tomorrow' },
              { text: 'Send itinerary toGroup B', due: 'In 2 days' },
            ].map((task, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '20px', height: '20px', border: '2px solid var(--border)', borderRadius: '6px' }}></div>
                <div>
                  <div style={{ fontSize: '14px' }}>{task.text}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{task.due}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
