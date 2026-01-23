import React, { useState } from 'react';
import { X, Calendar, Phone, Mail, User, Tag as TagIcon, MoreHorizontal } from 'lucide-react';
import styles from './AmoDealPanel.module.css';
import { Deal, Message } from '@/types/crm';
import { format } from 'date-fns';

interface Props {
    deal: Deal;
    onClose: () => void;
}

export default function AmoDealPanel({ deal, onClose }: Props) {
    const [messages, setMessages] = useState<Message[]>(deal.history || []);
    const [input, setInput] = useState('');

    const sendMessage = () => {
        if (!input.trim()) return;
        const newMsg: Message = {
            id: Date.now().toString(),
            type: 'note',
            author: 'You',
            text: input,
            created_at: Date.now(),
            direction: 'out'
        };
        setMessages([...messages, newMsg]);
        setInput('');
    };

    return (
        <div className={styles.panelOverlay} onClick={onClose}>
            <div className={styles.panelContainer} onClick={e => e.stopPropagation()}>

                {/* Header */}
                <div className={styles.header}>
                    <div className={styles.titleSection}>
                        <div style={{ fontSize: '12px', background: '#ccc', padding: '2px 6px', borderRadius: '4px', color: 'white', fontWeight: 'bold' }}>#{deal.id}</div>
                        <input defaultValue={deal.title} className={styles.titleInput} />
                    </div>
                    <div style={{ display: 'flex', gap: '16px' }}>
                        <button style={{ background: 'none', border: 'none', color: '#8c9fa6', cursor: 'pointer' }}><MoreHorizontal /></button>
                        <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#8c9fa6', cursor: 'pointer' }}><X /></button>
                    </div>
                </div>

                {/* Body */}
                <div className={styles.body}>

                    {/* Left Sidebar (Data Fields) */}
                    <div className={styles.sidebarLeft}>
                        <div className={styles.sectionHeader}>Main Info</div>

                        <div className={styles.fieldRow}>
                            <div className={styles.fieldLabel}>Budget</div>
                            <div style={{ display: 'flex', gap: '5px' }}>
                                <input defaultValue={deal.price} className={styles.fieldValue} style={{ width: '70%' }} />
                                <span style={{ paddingTop: '6px', color: '#888' }}>{deal.currency}</span>
                            </div>
                        </div>

                        <div className={styles.fieldRow}>
                            <div className={styles.fieldLabel}>Responsible</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingTop: '4px' }}>
                                <div style={{ width: 20, height: 20, borderRadius: '50%', background: '#6ccb5f', color: 'white', fontSize: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>A</div>
                                <span style={{ fontSize: '13px', fontWeight: 500, color: '#4c8bf5', cursor: 'pointer', borderBottom: '1px dashed #4c8bf5' }}>{deal.responsible}</span>
                            </div>
                        </div>

                        <div className={styles.fieldRow} style={{ marginTop: '10px' }}>
                            <div className={styles.fieldLabel}>Tags</div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
                                {deal.tags.map(tag => (
                                    <span key={tag.id} style={{ background: tag.color, color: 'white', fontSize: '11px', padding: '2px 8px', borderRadius: '4px' }}>
                                        {tag.name}
                                    </span>
                                ))}
                                <span style={{ color: '#8c9fa6', fontSize: '11px', cursor: 'pointer', padding: '2px 5px', border: '1px dashed #ccc', borderRadius: '4px' }}>+ add</span>
                            </div>
                        </div>

                        <div className={styles.sectionHeader}>Contact</div>
                        <div style={{ background: '#fff', border: '1px solid #e0e6ed', borderRadius: '4px', padding: '10px' }}>
                            <div style={{ fontWeight: 'bold', fontSize: '13px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <User size={14} color="#8c9fa6" />
                                {deal.contact_name}
                            </div>
                            {deal.contact_phone && (
                                <div style={{ fontSize: '13px', color: '#313942', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <Phone size={13} color="#8c9fa6" />{deal.contact_phone}
                                </div>
                            )}
                            {deal.contact_company && (
                                <div style={{ fontSize: '12px', color: '#8c9fa6' }}>{deal.contact_company}</div>
                            )}
                        </div>

                        <div className={styles.sectionHeader}>Custom Fields</div>
                        {deal.fields.map(f => (
                            <div key={f.key} className={styles.fieldRow}>
                                <div className={styles.fieldLabel}>{f.label}</div>
                                <input defaultValue={f.value} className={styles.fieldValue} />
                            </div>
                        ))}

                    </div>

                    {/* Right Main Area (Feed) */}
                    <div className={styles.mainArea}>
                        <div style={{ padding: '0 24px', height: '48px', borderBottom: '1px solid #eee', display: 'flex', alignItems: 'center', gap: '20px' }}>
                            <span style={{ fontSize: '13px', fontWeight: 600, color: '#313942', borderBottom: '2px solid #4c8bf5', padding: '14px 0', cursor: 'pointer' }}>Timeline</span>
                            <span style={{ fontSize: '13px', fontWeight: 500, color: '#8c9fa6', cursor: 'pointer' }}>Tasks (0)</span>
                            <span style={{ fontSize: '13px', fontWeight: 500, color: '#8c9fa6', cursor: 'pointer' }}>Stats</span>
                        </div>

                        <div className={styles.feedScroll}>
                            {messages.length === 0 && (
                                <div style={{ textAlign: 'center', color: '#ccc', marginTop: '40px' }}>No history yet</div>
                            )}
                            {messages.map((msg, i) => (
                                <div key={msg.id || i} className={styles.feedItem}>
                                    {i === 0 || (new Date(messages[i - 1].created_at).getDate() !== new Date(msg.created_at).getDate()) ? (
                                        <div className={styles.itemDate}>{format(msg.created_at, 'dd MMMM yyyy')}</div>
                                    ) : null}

                                    {msg.type === 'system' ? (
                                        <div className={styles.msgSystem}>{msg.text}</div>
                                    ) : (
                                        <div style={{ display: 'flex', gap: '10px', flexDirection: msg.direction === 'out' ? 'row-reverse' : 'row' }}>
                                            <div style={{ width: 24, height: 24, borderRadius: '50%', background: msg.direction === 'out' ? '#6ccb5f' : '#ccc', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', color: 'white', flexShrink: 0 }}>
                                                {msg.author[0]}
                                            </div>
                                            <div className={`${styles.msgBubble} ${msg.direction === 'out' ? styles.msgOut : styles.msgIn}`}>
                                                <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '2px', color: msg.direction === 'out' ? '#5c8692' : '#313942' }}>{msg.author}</div>
                                                {msg.text}
                                                <div style={{ fontSize: '10px', color: '#999', textAlign: 'right', marginTop: '4px' }}>
                                                    {format(msg.created_at, 'HH:mm')}
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        <div className={styles.inputArea}>
                            <div style={{ display: 'flex', gap: '10px', marginBottom: '8px' }}>
                                <span style={{ fontSize: '12px', fontWeight: 600, color: '#4c8bf5', cursor: 'pointer' }}>Note</span>
                                <span style={{ fontSize: '12px', fontWeight: 600, color: '#313942', cursor: 'pointer' }}>Task</span>
                                <span style={{ fontSize: '12px', fontWeight: 600, color: '#313942', cursor: 'pointer' }}>SMS</span>
                                <span style={{ fontSize: '12px', fontWeight: 600, color: '#313942', cursor: 'pointer' }}>Email</span>
                            </div>
                            <textarea
                                className={styles.chatInput}
                                placeholder="Type your note or message..."
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={e => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        sendMessage();
                                    }
                                }}
                            />
                            <button className={styles.sendButton} onClick={sendMessage}>Send</button>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    );
}
