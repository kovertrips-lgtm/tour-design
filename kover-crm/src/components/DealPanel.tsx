import React, { useState } from 'react';
import { X, User, Phone, Mail, Calendar, CheckSquare, MessageSquare, Send } from 'lucide-react';
import styles from './DealPanel.module.css';
import { Deal, Task, Note } from '@/types/crm';

interface DealPanelProps {
    deal: Deal;
    onClose: () => void;
}

export default function DealPanel({ deal, onClose }: DealPanelProps) {
    const [activeTab, setActiveTab] = useState<'feed' | 'info'>('feed');
    const [noteInput, setNoteInput] = useState('');

    return (
        <div className={styles.overlay} onClick={onClose}>
            <div className={styles.panel} onClick={e => e.stopPropagation()}>

                {/* Header */}
                <div className={styles.header}>
                    <div style={{ flex: 1, marginRight: '20px' }}>
                        <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>
                            Deal #{deal.id} • created {deal.created_at}
                        </div>
                        <input
                            defaultValue={deal.title}
                            className={styles.titleInput}
                        />
                        <div className={styles.badges}>
                            {deal.tags.map(tag => (
                                <span key={tag.id} className={styles.badge} style={{ background: `${tag.color}20`, color: tag.color, border: `1px solid ${tag.color}40` }}>
                                    {tag.name}
                                </span>
                            ))}
                            <span className={styles.badge} style={{ background: '#3b82f620', color: '#3b82f6', border: '1px solid #3b82f640' }}>
                                {deal.status}
                            </span>
                        </div>
                    </div>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                        <X size={24} />
                    </button>
                </div>

                <div className={styles.body}>
                    {/* Left Sidebar: Fields */}
                    <div className={styles.leftSidebar}>

                        <div className={styles.fieldGroup}>
                            <label className={styles.label}>Budget</label>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                <input className={styles.input} defaultValue={deal.price} style={{ flex: 1 }} />
                                <div style={{
                                    background: 'var(--bg-card)',
                                    padding: '10px',
                                    borderRadius: '6px',
                                    border: '1px solid var(--border)',
                                    color: 'var(--text-muted)'
                                }}>
                                    {deal.currency}
                                </div>
                            </div>
                        </div>

                        <div className={styles.fieldGroup}>
                            <label className={styles.label}>Main Contact</label>
                            <div style={{ background: 'var(--bg-card)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                                    <div className={styles.avatar}><User size={14} /></div>
                                    <div style={{ fontWeight: 600 }}>{deal.contact.name}</div>
                                </div>
                                {deal.contact.phone && (
                                    <div style={{ display: 'flex', gap: '8px', fontSize: '13px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                                        <Phone size={14} /> {deal.contact.phone}
                                    </div>
                                )}
                                {deal.contact.email && (
                                    <div style={{ display: 'flex', gap: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
                                        <Mail size={14} /> {deal.contact.email}
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className={styles.fieldGroup}>
                            <label className={styles.label}>Custom Fields</label>
                            <input className={styles.input} placeholder="Source (e.g. Instagram)" style={{ marginBottom: '8px' }} />
                            <input className={styles.input} placeholder="Tour Dates" />
                        </div>

                    </div>

                    {/* Right Content: Feed */}
                    <div className={styles.mainContent}>
                        <div className={styles.tabs}>
                            <div className={`${styles.tab} ${activeTab === 'feed' ? styles.activeTab : ''}`} onClick={() => setActiveTab('feed')}>
                                Timeline
                            </div>
                            <div className={`${styles.tab} ${activeTab === 'info' ? styles.activeTab : ''}`} onClick={() => setActiveTab('info')}>
                                Tasks ({deal.tasks.length})
                            </div>
                        </div>

                        <div className={styles.feed}>
                            {deal.notes.length === 0 && (
                                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px' }}>
                                    No history yet. Start writing a note!
                                </div>
                            )}

                            {deal.notes.map(note => (
                                <div key={note.id} className={styles.noteItem}>
                                    <div className={styles.avatar}>
                                        {note.type === 'system' ? '🤖' : note.author[0]}
                                    </div>
                                    <div className={styles.noteContent}>
                                        <div className={styles.noteMeta}>
                                            <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{note.author}</span>
                                            <span>{note.date}</span>
                                        </div>
                                        <div style={{ fontSize: '14px', lineHeight: '1.4' }}>{note.text}</div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Input Area */}
                        <div className={styles.inputArea}>
                            <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                                <button style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '13px', display: 'flex', gap: '6px', alignItems: 'center' }}>
                                    <MessageSquare size={16} /> Note
                                </button>
                                <button style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '13px', display: 'flex', gap: '6px', alignItems: 'center' }}>
                                    <CheckSquare size={16} /> Task
                                </button>
                            </div>
                            <div style={{ position: 'relative' }}>
                                <textarea
                                    placeholder="Click to add a note or call summary..."
                                    className={styles.input}
                                    style={{ minHeight: '80px', resize: 'none', paddingRight: '40px' }}
                                    value={noteInput}
                                    onChange={(e) => setNoteInput(e.target.value)}
                                />
                                <button
                                    style={{
                                        position: 'absolute',
                                        right: '10px',
                                        bottom: '10px',
                                        background: noteInput ? 'var(--primary)' : 'var(--bg-card-hover)',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '4px',
                                        width: '32px',
                                        height: '32px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        cursor: noteInput ? 'pointer' : 'default',
                                        transition: 'all 0.2s'
                                    }}
                                >
                                    <Send size={16} />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
