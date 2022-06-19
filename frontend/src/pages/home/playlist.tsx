import { IRouteComponentProps } from 'umi'
import React, { useState } from 'react';
import styles from './playlist.less';
import globalStyles from '../../style/global.less'
import { Card, List } from 'antd';
import { cloudMusicFetch } from '../../http/cloudMusic'
import { formatPicUrl } from '../../utils/format'

const { Meta } = Card
interface IPersonalized {
  id: number,
  name: string,
  picUrl: string,
}

let data = new Array<IPersonalized>();

cloudMusicFetch('/personalized').then(res => {
  console.log(res)
  data = res.result
})

export default function Page({ history }: IRouteComponentProps) {
  // const [data, setData] = useState(new Array<IPersonalized>());
  return (
    <List
      grid={{ gutter: 8, column: 5 }}
      dataSource={data}
      renderItem={item => (
        <List.Item>
          <Card hoverable cover={<img src={formatPicUrl(item.picUrl)} />}
            onClick={() => history.push(`/player/playlist?id=${item.id}`)}>
            <Meta className={globalStyles.meta} title={item.name} />
          </Card>
        </List.Item>
      )}
    />
  );
}