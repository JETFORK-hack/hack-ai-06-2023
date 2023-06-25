import { Typography, Upload, UploadProps, message } from 'antd';
import { basePath } from '../providers/env';
import { useEffect } from 'react';
import axios from 'axios';
import { Uploader } from '../components/Uploader/Uploader';

const { Link } = Typography;

const { Dragger } = Upload;

const props: UploadProps = {
    name: 'files',
    accept: '.pdf,.zip,.rar,.7z',
    multiple: true,
    action: basePath + '/api/v1/upload/files',
    onChange(info) {
        const { status } = info.file;
        if (status !== 'uploading') {
            console.log(info.file, info.fileList);
        }
        if (status === 'done') {
            message.success(`${info.file.name} file uploaded successfully.`);
        } else if (status === 'error') {
            message.error(`${info.file.name} file upload failed.`);
        }
    },
    onDrop(e) {
        console.log('Dropped files', e.dataTransfer.files);
    },
};

export const Loading = (): JSX.Element => {


    useEffect(() => {
        axios.get(basePath + '/api/v1/hello-world')
            .then((response) => {
                console.log(response);
            })
    }, []);

    return (
        <>
            <h1>Проверка</h1>
            <div style={{ textAlign: 'right' }}>
                <Link href="https://jetfork.ru/pdfs/%D0%9A%D1%83%D0%B7%D0%B1-183267_%D0%9A%D0%A0%D0%90%D0%A1%E2%80%93%D0%98%D0%AD%D0%981_%D0%B8%D0%B7%D0%BC.6.00256-21_%D0%9A%D0%A0%D0%AD-26756.pdf" target="_blank">
                    Скачать пробный файл
                </Link>
            </div>
            <br />

            {/* <Dragger {...props}>
                <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                </p>
                <p className="ant-upload-text">Кликните или перетащите файлы в эту область для загрузки</p>
                <p className="ant-upload-hint">
                    Поддержка одиночной или массовой загрузки.
                    Разрешенные форматы: .pdf или .zip, .rar, .7z (с файлами .pdf внутри).
                </p>
            </Dragger> */}
            <Uploader />
        </>
    )
};