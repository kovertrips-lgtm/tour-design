import React, { useState } from "react";
import { List, Card, Table, Tag, Space, Typography, Button, Statistic, Row, Col } from "antd";
import {
    PlusOutlined,
    ArrowUpOutlined,
    ArrowDownOutlined,
    WalletOutlined,
    BankOutlined,
    FilterOutlined
} from "@ant-design/icons";
import { Text } from "@/components";

const { Title } = Typography;

// Mock Data mimicking Adesk structure
const MOCK_TRANSACTIONS = [
    {
        id: 1,
        date: "23.01.2026",
        category: "Продажа тура",
        description: "Оплата за тур Альпы 2026 (Ivanov)",
        amount: 52000,
        type: "income",
        account: "Сбербанк",
    },
    {
        id: 2,
        date: "23.01.2026",
        category: "Маркетинг",
        description: "Реклама Instagram",
        amount: -15000,
        type: "expense",
        account: "Тинькофф",
    },
    {
        id: 3,
        date: "22.01.2026",
        category: "Продажа тура",
        description: "Предоплата Париж (Petrov)",
        amount: 30000,
        type: "income",
        account: "Касса",
    },
    {
        id: 4,
        date: "21.01.2026",
        category: "Зарплата",
        description: "Аванс менеджеру",
        amount: -45000,
        type: "expense",
        account: "Сбербанк",
    },
    {
        id: 5,
        date: "20.01.2026",
        category: "Офис",
        description: "Аренда коворкинга",
        amount: -12000,
        type: "expense",
        account: "Тинькофф",
    },
];

const ACCOUNTS = [
    { name: "Всего денег", balance: 1345000, currency: "₽", icon: <WalletOutlined />, color: "#52c41a" },
    { name: "Сбербанк (ООО)", balance: 850000, currency: "₽", icon: <BankOutlined />, color: "#1890ff" },
    { name: "Тинькофф (ИП)", balance: 420000, currency: "₽", icon: <BankOutlined />, color: "#faad14" },
    { name: "Наличные (Касса)", balance: 75000, currency: "₽", icon: <WalletOutlined />, color: "#722ed1" },
];

export const FinanceListPage = () => {
    const [data] = useState(MOCK_TRANSACTIONS);

    return (
        <div className="page-container">
            {/* Header Section */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
                <Title level={2} style={{ margin: 0 }}>Финансы</Title>
                <Space>
                    <Button icon={<FilterOutlined />}>Фильтр</Button>
                    <Button type="primary" icon={<PlusOutlined />}>Добавить операцию</Button>
                </Space>
            </div>

            {/* Accounts Summary (Adesk Style) */}
            <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
                {ACCOUNTS.map((acc, idx) => (
                    <Col xs={24} sm={12} xl={6} key={idx}>
                        <Card bodyStyle={{ padding: "20px 24px" }} style={{ height: "100%", borderRadius: 12 }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                                <div style={{
                                    backgroundColor: `${acc.color}20`,
                                    padding: 8,
                                    borderRadius: "50%",
                                    color: acc.color,
                                    display: "flex"
                                }}>
                                    {acc.icon}
                                </div>
                                <Text size="sm" style={{ color: "#8c8c8c" }}>{acc.name}</Text>
                            </div>
                            <div style={{ fontSize: 24, fontWeight: 700, fontFamily: "monospace" }}>
                                {acc.balance.toLocaleString()} {acc.currency}
                            </div>
                        </Card>
                    </Col>
                ))}
            </Row>

            {/* Main Transactions Table */}
            <Card
                bodyStyle={{ padding: 0 }}
                style={{ borderRadius: 12, overflow: "hidden" }}
            >
                <Table
                    dataSource={data}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                >
                    <Table.Column
                        title="Дата"
                        dataIndex="date"
                        width={120}
                        render={(text) => <Text style={{ color: "#8c8c8c" }}>{text}</Text>}
                    />
                    <Table.Column
                        title="Категория"
                        dataIndex="category"
                        render={(text) => <Tag>{text}</Tag>}
                    />
                    <Table.Column
                        title="Описание"
                        dataIndex="description"
                        render={(text, record: any) => (
                            <div>
                                <div style={{ fontWeight: 500 }}>{text}</div>
                                <div style={{ fontSize: 12, color: "#bfbfbf" }}>{record.account}</div>
                            </div>
                        )}
                    />
                    <Table.Column
                        title="Сумма"
                        dataIndex="amount"
                        align="right"
                        render={(amount, record: any) => (
                            <Text
                                strong
                                style={{
                                    color: record.type === 'income' ? '#52c41a' : '#f5222d',
                                    fontSize: 16
                                }}
                            >
                                {amount > 0 ? '+' : ''}{amount.toLocaleString()} ₽
                            </Text>
                        )}
                    />
                </Table>
            </Card>
        </div>
    );
};
