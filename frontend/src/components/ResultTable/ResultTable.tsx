import { Alert, Button, Progress, Space, Table, Tooltip, Typography, message } from 'antd';
import { useParams } from 'react-router-dom';
import * as diff from "diff";
import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { CSVDownload, CSVLink } from "react-csv";
import { basePath } from '../../providers/env';
import { CheckCircleTwoTone, CloseCircleFilled, CloseCircleTwoTone, LoadingOutlined, SettingFilled } from '@ant-design/icons';

const { Title } = Typography;

const delay = 5;

const styles = {
    added: {
        color: "green",
        backgroundColor: "#b5efdb"
    },
    removed: {
        color: "red",
        backgroundColor: "#fec4c0"
    }
};

const DiffColor = ({ string1 = "", string2 = "", mode = "characters" }) => {
    let groups: any[] = [];

    if (mode === "characters") groups = diff.diffChars(string1, string2, { ignoreCase: true });
    if (mode === "words") groups = diff.diffWords(string1, string2, { ignoreCase: true });

    const mappedNodes = groups.map(group => {
        const { value, added, removed } = group;
        let nodeStyles;
        if (added) nodeStyles = styles.added;
        if (removed) nodeStyles = styles.removed;
        return <span style={nodeStyles}>{value}</span>;
    });

    return <span>{mappedNodes}</span>;
};

interface RemarkWithFileName {
    id: number;
    file_id: number;
    file_name: string;
    page_num: number;
    golden_name: string;
    targets: string;
    candidate: string;
    probability: number;
    similarity: number;
    is_correct?: boolean;
}

type Response = {
    status: 'SUCCESS',
    result: RemarkWithFileName[],
} | {
    status: 'FAILURE',
    message: string,
} | {
    status: 'PENDING',
} | {
    status: 'STARTED',
} | {
    status: 'RETRY',
} | {
    status: 'PROGRESS',
    detail: {
        done: number,
        total: number,
    }
}


export const ResultTable = () => {
    const { id } = useParams();
    const [data, setData] = useState<RemarkWithFileName[]>([]);
    const [status, setStatus] = useState<string>('PENDING');
    const [isLoading, setIsLoading] = useState(false);
    const [progress, setProgress] = useState<{ done: number, total: number, } | null>(null);
    const [errMessage, setErrMessage] = useState<string | null>(null);
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

    const timer = useRef<number | null>(null); // we can save timer in useRef and pass it to child


    const selectedRows = data.filter((item) => selectedRowKeys.includes(item.id));

    const setFeedback = (id: number, is_correct: boolean) => {
        const newData = data.map((item) => {
            if (item.id === id) {
                return { ...item, is_correct };
            }
            return item;
        });
        setData(newData);
        axios.patch(`${basePath}/api/v1/upload/remark/${id}`, { is_correct })
            .then((response) => {
                console.log(response);
            }
            ).catch((error) => {
                console.log(error);
            });

    }

    const columns = [
        {
            title: 'Название файла',
            dataIndex: 'file_name',
            key: 'file_name',
            filterSearch: true,
            onFilter: (value: string, record: RemarkWithFileName) => record.file_name.startsWith(value),
        },
        {
            title: 'Номер страницы',
            dataIndex: 'page_num',
            key: 'page_num',
            sorter: (a: RemarkWithFileName, b: RemarkWithFileName) => a.page_num - b.page_num,
        },
        {
            title: 'Эталонная сущность',
            dataIndex: 'golden_name',
            key: 'golden_name',
            render(text: string) {
                // return <ReactDiffViewer oldValue={record.receivedName} newValue={record.recognizedName} splitView={false} />
                return <div dangerouslySetInnerHTML={{ __html: text }} />
            }
        },
        {
            title: 'Распознанное наименование объекта',
            dataIndex: 'candidate',
            key: 'candidate'
        },
        {
            title: 'Совпадения по тексту документа',
            dataIndex: 'candidate',
            key: 'diff',
            render: (text: string, record: RemarkWithFileName) => {
                return DiffColor({ string1: record.candidate, string2: record.golden_name },);
            }
        },
        {
            title: 'Уверенность в совпадении',
            dataIndex: 'probability',
            key: 'probability',
            render: (text: string, record: RemarkWithFileName) => {
                return record.probability.toFixed(4);
            },
            sorter: (a: RemarkWithFileName, b: RemarkWithFileName) => a.probability - b.probability,
        },
        {
            title: 'Похожесть',
            dataIndex: 'similarity',
            key: 'similarity',
            render: (text: string, record: RemarkWithFileName) => {
                return record.similarity.toFixed(2);
            },
            sorter: (a: RemarkWithFileName, b: RemarkWithFileName) => a.similarity - b.similarity,
        },
        {
            title: 'Действия',
            key: 'action',
            render: (_: any, record: RemarkWithFileName) => (
                record.is_correct === undefined ?
                    <Space size="middle"
                        align='center'>
                        <Tooltip title="Отметить как верный">
                            <Button icon={<CheckCircleTwoTone twoToneColor="#52c41a" />} onClick={() => setFeedback(record.id, true)} />
                        </Tooltip>
                        <Tooltip title="Отметить как ошибочный">
                            <Button icon={<CloseCircleTwoTone twoToneColor="#eb2f96" />} onClick={() => setFeedback(record.id, false)} />
                        </Tooltip>
                    </Space>
                    : record.is_correct ?
                        <CheckCircleTwoTone twoToneColor="#52c41a" />
                        : <CloseCircleTwoTone twoToneColor="#eb2f96" />
            ),
            filters: [
                {
                    text: 'Только верные',
                    value: true,
                },
                {
                    text: 'Только ошибочные',
                    value: false,
                },
                {
                    text: 'Не отмеченные',
                    value: null,
                },
            ],
            filterSearch: true,
            onFilter: (value: boolean, record: RemarkWithFileName) => value === null ? record.is_correct === undefined : record.is_correct === value,
        },
    ];


    useEffect(() => {
        timer.current = setInterval(() => getData(), delay * 1000);
        return () => {
            clearInterval(timer.current || undefined);
        };
    }, []);

    const getData = () => {
        setIsLoading(true);
        setErrMessage(null);
        axios.get<Response>(basePath + '/api/v1/upload/result/' + id)
            .then((response) => {
                clearInterval(timer.current || undefined);
                if (response.data.status === 'SUCCESS') {
                    setData(response.data.result);
                    setSelectedRowKeys([]);
                }
                setIsLoading(false);
                setStatus(response.data.status);
                if (response.data.status === 'PENDING' || response.data.status === 'PROGRESS') {
                    timer.current = setInterval(() => getData(), delay * 1000);
                }
                if (response.data.status === 'PROGRESS') {
                    setProgress(response.data.detail);
                }
                if (response.data.status === 'FAILURE') {
                    setErrMessage(response.data.message);
                }
            })
            .catch((error) => {
                setIsLoading(false);
                message.error(`Не удалось получить информацию о проверке: ${error.message}`);
                setStatus('FAILURE');
            });
    };


    useEffect(() => {
        getData();
    }, [id]);

    const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
        console.log('selectedRowKeys changed: ', newSelectedRowKeys);
        setSelectedRowKeys(newSelectedRowKeys);
    };

    const rowSelection = {
        selectedRowKeys,
        onChange: onSelectChange,
    };

    const hasSelected = selectedRowKeys.length > 0;

    return (
        <>
            <Title>Результаты проверки</Title>
            {status === 'PROGRESS' && <> <Alert
                type="warning" showIcon icon={<SettingFilled spin />}
                message="Заявка в процессе обработки"
                description={<p>
                    Пожалуйста, подождите, пока заявка будет обработана. Это может занять некоторое время.
                    <br />Страница будет обновлена автоматически.</p>}
            />
                <Progress percent={progress ? (progress.done / progress.total * 100).toFixed(2) : 0}
                    status="active" strokeColor={{ from: '#108ee9', to: '#87d068' }} />
            </>}

            {status === 'PENDING' &&
                <Alert
                    type="warning" showIcon icon={<LoadingOutlined spin />}
                    message="Заявка в очереди на обработку"
                    description={<p>
                        Пожалуйста, подождите, пока заявка будет обработана. Это может занять некоторое время.
                        <br />Страница будет обновлена автоматически.</p>}
                />}

            {status === 'SUCCESS' &&
                <div>
                    <div style={{ marginBottom: 16 }}>
                        <Button type="primary" onClick={() => console.log('clicked')} disabled={!hasSelected} loading={isLoading}>
                            <CSVLink data={selectedRows} filename={"jetfork_export.csv"}>Выгрузить результаты</CSVLink>
                        </Button>
                        {/* <CSVDownload data={selectedRows} target="_blank" /> */}

                        <span style={{ marginLeft: 8 }}>
                            {hasSelected ? `Выделено ${selectedRowKeys.length}` : ''}
                        </span>
                    </div>
                    <Table dataSource={data} columns={columns}
                        loading={isLoading} pagination={{ pageSize: 15 }}
                        scroll={{ x: true }}
                        rowSelection={rowSelection} rowKey='id' />
                </div>}


            {status === 'FAILURE' && <Alert
                type="error" showIcon icon={<CloseCircleFilled />}
                message="Заявка не обработана"
                description={<p><b>{errMessage}</b>{errMessage ? <><br /><br /></> : ''}
                    Пожалуйста, попробуйте еще раз</p>}
            />}
        </>
    );
}
