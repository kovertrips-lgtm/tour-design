import React, { useState } from "react";
import {
    Card, Table, Tag, Typography, Button, Row, Col, Statistic, DatePicker, Segmented, Modal, Form, Input, Select, InputNumber, Divider
} from "antd";
import {
    PlusOutlined,
    MinusOutlined,
    SwapOutlined,
    ArrowUpOutlined,
    ArrowDownOutlined,
    WalletOutlined,
    BankOutlined,
    CalendarOutlined,
    CheckCircleFilled,
    ClockCircleOutlined
} from "@ant-design/icons";
import { Area } from "@ant-design/plots";
import { Text } from "@/components";
import dayjs from "dayjs";

const { Title } = Typography;
const { RangePicker } = DatePicker;

// --- MOCK DATA ---
const MOCK_STATS = [
    { title: "Поступления", value: 1250000, trend: 12, color: "#52c41a", prefix: "+" },
    { title: "Расходы", value: 840000, trend: -5, color: "#f5222d", prefix: "-" },
    { title: "Прибыль", value: 410000, trend: 20, color: "#1890ff", prefix: "" },
    { title: "Деньги в бизнесе", value: 3450000, trend: 0, color: "#722ed1", prefix: "" },
];

const MOCK_ACCOUNTS = [
    { name: "Сбербанк (ООО)", balance: 1850000, type: "bank" },
    { name: "Тинькофф (ИП)", balance: 1420000, type: "bank" },
    { name: "Касса", balance: 180000, type: "cash" },
];

const MOCK_TRANSACTIONS = [
    { id: 1, date: "23.01.2026", category: "Продажа тура", description: "Оплата за Альпы (Ivanov)", amount: 52000, type: "income", account: "Сбербанк", project: "Альпы 2026" },
    { id: 2, date: "23.01.2026", category: "Маркетинг", description: "Facebook Ads", amount: -15000, type: "expense", account: "Тинькофф", project: "Общее" },
    { id: 3, date: "22.01.2026", category: "Аренда", description: "Офис Январь", amount: -45000, type: "expense", account: "Сбербанк", project: "Офис" },
    { id: 4, date: "21.01.2026", category: "Продажа тура", description: "Предоплата Париж (Petrov)", amount: 30000, type: "income", account: "Касса", project: "Париж Весна" },
    { id: 5, date: "20.01.2026", category: "Зарплата", description: "Аванс менеджеру", amount: -25000, type: "expense", account: "Тинькофф", project: "Штат" },
];

// Mock Chart Data
const CHART_DATA = (() => {
    const data = [];
    let balance = 3000000;
    for (let i = 30; i >= 0; i--) {
        const date = dayjs().subtract(i, 'day').format('YYYY-MM-DD');
        const change = Math.floor(Math.random() * 200000) - 80000;
        balance += change;
        data.push({ date, value: balance });
    }
    return data;
})();

export const FinanceListPage = () => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [opType, setOpType] = useState<"income" | "expense" | "transfer">("income");

    const openModal = (type: "income" | "expense" | "transfer") => {
        setOpType(type);
        setIsModalOpen(true);
    };

    const chartConfig = {
        data: CHART_DATA,
        xField: 'date',
        yField: 'value',
        xAxis: {
            range: [0, 1],
            tickCount: 5,
        },
        areaStyle: () => {
            return {
                fill: 'l(270) 0:#ffffff 0.5:#dbeafe 1:#1677ff',
            };
        },
        line: {
            color: '#1677ff',
        },
        smooth: true,
        height: 300,
        autoFit: true,
    };

    return (
        <div className="page-container" style={{ maxWidth: 1600, margin: "0 auto" }}>
            {/* HEADER */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
                <div>
                    <Title level={2} style={{ margin: 0, fontWeight: 700 }}>Финансы</Title>
                    <Text type="secondary">Обзор денежных потоков компании</Text>
                </div>
                <div style={{ display: 'flex', gap: 12 }}>
                    <RangePicker style={{ borderRadius: 8 }} />
                    <Button icon={<CalendarOutlined />}>Этот месяц</Button>
                </div>
            </div>

            {/* KPI CARDS */}
            <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
                {MOCK_STATS.map((stat, idx) => (
                    <Col xs={24} sm={12} xl={6} key={idx}>
                        <Card
                            bordered={false}
                            bodyStyle={{ padding: "24px" }}
                            style={{ borderRadius: 16, boxShadow: "0 4px 20px rgba(0,0,0,0.03)" }}
                        >
                            <div style={{ color: "#8c8c8c", fontSize: 13, fontWeight: 600, textTransform: "uppercase", letterSpacing: 0.5 }}>
                                {stat.title}
                            </div>
                            <div style={{ fontSize: 28, fontWeight: 800, margin: "8px 0", color: stat.color }}>
                                {stat.prefix}{stat.value.toLocaleString()} ₽
                            </div>
                            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                                {stat.trend > 0 ? <ArrowUpOutlined style={{ color: "#52c41a" }} /> : <ArrowDownOutlined style={{ color: "#f5222d" }} />}
                                <Text size="sm" style={{ color: stat.trend > 0 ? "#52c41a" : "#f5222d", fontWeight: 500 }}>
                                    {Math.abs(stat.trend)}% к прошлому месяцу
                                </Text>
                            </div>
                        </Card>
                    </Col>
                ))}
            </Row>

            {/* CHART & ACCOUNTS */}
            <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
                <Col xs={24} xl={16}>
                    <Card
                        title={<span style={{ fontSize: 18, fontWeight: 700 }}>Динамика остатков</span>}
                        bordered={false}
                        style={{ borderRadius: 16, height: '100%', boxShadow: "0 4px 20px rgba(0,0,0,0.03)" }}
                    >
                        <Area {...chartConfig} />
                    </Card>
                </Col>
                <Col xs={24} xl={8}>
                    <Card
                        title={<span style={{ fontSize: 18, fontWeight: 700 }}>Счета</span>}
                        bordered={false}
                        style={{ borderRadius: 16, height: '100%', boxShadow: "0 4px 20px rgba(0,0,0,0.03)" }}
                        extra={<Button type="link">Управление</Button>}
                    >
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                            {MOCK_ACCOUNTS.map((acc, idx) => (
                                <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', borderBottom: idx !== MOCK_ACCOUNTS.length - 1 ? '1px solid #f0f0f0' : 'none' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                        <div style={{
                                            width: 40, height: 40, borderRadius: 12,
                                            backgroundColor: acc.type === 'bank' ? '#e6f7ff' : '#f9f0ff',
                                            color: acc.type === 'bank' ? '#1890ff' : '#722ed1',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            fontSize: 18
                                        }}>
                                            {acc.type === 'bank' ? <BankOutlined /> : <WalletOutlined />}
                                        </div>
                                        <div>
                                            <div style={{ fontWeight: 600, fontSize: 15 }}>{acc.name}</div>
                                            <div style={{ fontSize: 12, color: '#8c8c8c' }}>Основной</div>
                                        </div>
                                    </div>
                                    <div style={{ fontWeight: 700, fontSize: 16 }}>{acc.balance.toLocaleString()} ₽</div>
                                </div>
                            ))}
                        </div>
                    </Card>
                </Col>
            </Row>

            {/* OPERATIONS SECTION */}
            <Card
                bordered={false}
                style={{ borderRadius: 16, boxShadow: "0 4px 20px rgba(0,0,0,0.03)" }}
                bodyStyle={{ padding: "0" }}
            >
                <div style={{ padding: "20px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #f0f0f0" }}>
                    <Title level={4} style={{ margin: 0 }}>Операции</Title>
                    <div style={{ display: 'flex', gap: 12 }}>
                        <Button
                            type="primary"
                            icon={<PlusOutlined />}
                            style={{ backgroundColor: "#52c41a", borderColor: "#52c41a", height: 40, borderRadius: 8, padding: "0 24px", fontWeight: 600 }}
                            onClick={() => openModal("income")}
                        >
                            Поступление
                        </Button>
                        <Button
                            type="primary"
                            icon={<MinusOutlined />}
                            danger
                            style={{ height: 40, borderRadius: 8, padding: "0 24px", fontWeight: 600 }}
                            onClick={() => openModal("expense")}
                        >
                            Расход
                        </Button>
                        <Button
                            icon={<SwapOutlined />}
                            style={{ height: 40, borderRadius: 8, padding: "0 24px", fontWeight: 600 }}
                            onClick={() => openModal("transfer")}
                        >
                            Перевод
                        </Button>
                    </div>
                </div>

                <Table
                    dataSource={MOCK_TRANSACTIONS}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                    rowClassName="finance-row"
                >
                    <Table.Column
                        title="Дата"
                        dataIndex="date"
                        width={120}
                        render={(text) => <div style={{ color: "#8c8c8c", fontWeight: 500 }}>{text}</div>}
                    />
                    <Table.Column
                        title="Тип / Категория"
                        dataIndex="category"
                        render={(text, record: any) => (
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <div style={{
                                    width: 8, height: 8, borderRadius: "50%",
                                    backgroundColor: record.type === 'income' ? '#52c41a' : '#f5222d'
                                }} />
                                <span style={{ fontWeight: 500 }}>{text}</span>
                            </div>
                        )}
                    />
                    <Table.Column
                        title="Описание"
                        dataIndex="description"
                        render={(text) => <span style={{ color: "#595959" }}>{text}</span>}
                    />
                    <Table.Column
                        title="Проект"
                        dataIndex="project"
                        render={(text) => (
                            <Tag>{text}</Tag>
                        )}
                    />
                    <Table.Column
                        title="Счет"
                        dataIndex="account"
                        render={(text) => <Tag color="blue">{text}</Tag>}
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
                                    fontSize: 16,
                                    fontVariantNumeric: "tabular-nums"
                                }}
                            >
                                {amount > 0 ? '+' : ''}{amount.toLocaleString()} ₽
                            </Text>
                        )}
                    />
                </Table>
            </Card>

            {/* ADD OPERATION MODAL */}
            <Modal
                open={isModalOpen}
                onCancel={() => setIsModalOpen(false)}
                title={null}
                footer={null}
                width={500}
                destroyOnClose
            >
                <div style={{ marginBottom: 24, textAlign: 'center' }}>
                    <Segmented
                        options={[
                            { label: 'Поступление', value: 'income', icon: <PlusOutlined /> },
                            { label: 'Расход', value: 'expense', icon: <MinusOutlined /> },
                            { label: 'Перевод', value: 'transfer', icon: <SwapOutlined /> },
                        ]}
                        value={opType}
                        onChange={(val: any) => setOpType(val)}
                        block
                        style={{ marginBottom: 24 }}
                    />
                    <Title level={3} style={{ margin: 0 }}>
                        {opType === 'income' ? 'Новое поступление' : opType === 'expense' ? 'Новый расход' : 'Новый перевод'}
                    </Title>
                </div>

                <Form layout="vertical" size="large">
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="Дата">
                                <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="Сумма">
                                <InputNumber
                                    style={{ width: '100%' }}
                                    formatter={value => `₽ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                                    parser={value => value!.replace(/\₽\s?|(,*)/g, '')}
                                    placeholder="0"
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Form.Item label={opType === 'transfer' ? "Списать со счета" : "Счет"}>
                        <Select
                            placeholder="Выберите счет"
                            options={[
                                { label: "Сбербанк (ООО)", value: "sber" },
                                { label: "Тинькофф (ИП)", value: "tinkoff" },
                                { label: "Касса", value: "cash" },
                            ]}
                        />
                    </Form.Item>

                    {opType === 'transfer' && (
                        <Form.Item label="Зачислить на счет">
                            <Select
                                placeholder="Выберите счет"
                                options={[
                                    { label: "Сбербанк (ООО)", value: "sber" },
                                    { label: "Тинькофф (ИП)", value: "tinkoff" },
                                    { label: "Касса", value: "cash" },
                                ]}
                            />
                        </Form.Item>
                    )}

                    {opType !== 'transfer' && (
                        <Form.Item label="Статья (Категория)">
                            <Select
                                placeholder="Выберите категорию"
                                options={[
                                    { label: "Продажа тура", value: "sales" },
                                    { label: "Маркетинг", value: "marketing" },
                                    { label: "Зарплата", value: "salary" },
                                    { label: "Офис", value: "office" },
                                ]}
                            />
                        </Form.Item>
                    )}

                    <Form.Item label="Проект (Сделка)">
                        <Select
                            placeholder="Привязать к сделке (необязательно)"
                            showSearch
                            options={[
                                { label: "Альпы 2026", value: "alps" },
                                { label: "Париж Весна", value: "paris" },
                            ]}
                        />
                    </Form.Item>

                    <Form.Item label="Комментарий">
                        <Input.TextArea rows={2} placeholder="Детали операции..." />
                    </Form.Item>

                    <Button type="primary" block size="large" onClick={() => setIsModalOpen(false)}>
                        Сохранить
                    </Button>
                </Form>
            </Modal>
        </div>
    );
};
