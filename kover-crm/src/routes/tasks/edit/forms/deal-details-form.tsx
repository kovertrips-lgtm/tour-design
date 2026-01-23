import { DatePicker, Form, Input, InputNumber, Select } from "antd";

export const DealDetailsForm = () => {
    return (
        <div style={{ padding: "12px 24px", borderBottom: "1px solid #f0f0f0" }}>
            <Form layout="vertical">
                <Form.Item label="Тур">
                    <Select
                        placeholder="Выберите тур"
                        options={[
                            { label: "Альпы 2026", value: "alps_2026" },
                            { label: "Париж Весна", value: "paris_spring" },
                            { label: "Норвегия Фьорды", value: "norway" },
                        ]}
                    />
                </Form.Item>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <Form.Item label="Стоимость тура" style={{ flex: 1 }}>
                        <InputNumber
                            style={{ width: '100%' }}
                            formatter={value => `₽ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                            parser={value => value!.replace(/\₽\s?|(,*)/g, '')}
                        />
                    </Form.Item>
                    <Form.Item label="Бюджет" style={{ flex: 1 }}>
                        <InputNumber
                            style={{ width: '100%' }}
                            formatter={value => `₽ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                            parser={value => value!.replace(/\₽\s?|(,*)/g, '')}
                        />
                    </Form.Item>
                </div>

                <div style={{ display: 'flex', gap: '12px' }}>
                    <Form.Item label="Вид залога" style={{ flex: 1 }}>
                        <Select placeholder="Выбрать" options={[{ label: "Частичный", value: "partial" }, { label: "Полный", value: "full" }]} />
                    </Form.Item>
                    <Form.Item label="Размер залога" style={{ flex: 1 }}>
                        <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                </div>

                <Form.Item label="Источник">
                    <Select
                        placeholder="Выбрать"
                        options={[
                            { label: "Instagram", value: "instagram" },
                            { label: "Telegram", value: "telegram" },
                            { label: "Рекомендация", value: "referral" },
                        ]}
                        defaultValue="instagram"
                    />
                </Form.Item>

                <Form.Item label="Контакты (Instagram)">
                    <Input prefix="@" placeholder="username" />
                </Form.Item>

                <Form.Item label="Telegram">
                    <Input prefix="@" placeholder="username" />
                </Form.Item>

                <Form.Item label="Номер паспорта">
                    <Input placeholder="AA 123456" />
                </Form.Item>

                <Form.Item label="Дата рождения">
                    <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" />
                </Form.Item>
            </Form>
        </div>
    );
};
