import { Alert, Progress, Table, Typography, message } from 'antd';
import { useParams } from 'react-router-dom';
import * as diff from "diff";
import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { basePath } from '../../providers/env';
import { CloseCircleFilled, LoadingOutlined, SettingFilled } from '@ant-design/icons';

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

const columns = [
    {
        title: 'Название файла',
        dataIndex: 'file_name',
        key: 'file_name',
    },
    {
        title: 'Номер страницы',
        dataIndex: 'page_num',
        key: 'page_num',
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
        }
    },
    {
        title: 'Похожесть',
        dataIndex: 'similarity',
        key: 'similarity',
        render: (text: string, record: RemarkWithFileName) => {
            return record.similarity.toFixed(2);
        }
    },
];

export const ResultTable = () => {
    const { id } = useParams();
    const [data, setData] = useState<RemarkWithFileName[]>([]);
    const [status, setStatus] = useState<string>('PENDING');
    const [isLoading, setIsLoading] = useState(false);
    const [progress, setProgress] = useState<{ done: number, total: number, } | null>(null);
    const [errMessage, setErrMessage] = useState<string | null>(null);

    const timer = useRef<number | null>(null); // we can save timer in useRef and pass it to child

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
                <Progress percent={progress ? progress.done / progress.total * 100 : 0}
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
                <Table dataSource={data} columns={columns} loading={isLoading} pagination={{ pageSize: 15 }} />}

            {status === 'FAILURE' && <Alert
                type="error" showIcon icon={<CloseCircleFilled />}
                message="Заявка не обработана"
                description={<p><b>{errMessage}</b>{errMessage ? <><br /><br /></> : ''}
                    Пожалуйста, попробуйте еще раз</p>}
            />}
        </>
    );
}
