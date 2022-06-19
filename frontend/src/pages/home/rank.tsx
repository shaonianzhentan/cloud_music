import { IRouteComponentProps } from 'umi'
import React, { useState } from 'react';
import styles from './rank.less';
import globalStyles from '../../style/global.less'
import { Card, List } from 'antd';
import { cloudMusicFetch, IToplist } from '../../http/cloudMusic'
import { formatPicUrl } from '../../utils/format'
const { Meta } = Card

let data = new Array<IToplist>();

cloudMusicFetch('/toplist').then(res => {
  data = res.list
})

export default function Page({ history }: IRouteComponentProps) {
  return (
    <List
      grid={{ gutter: 8, column: 5 }}
      dataSource={data}
      renderItem={item => (
        <List.Item>
          <Card hoverable cover={<img src={formatPicUrl(item.coverImgUrl)} />}
            onClick={() => history.push(`/player/playlist?id=${item.id}`)}>
            <Meta className={styles.meta} title={item.name} />
          </Card>
        </List.Item>
      )}
    />
  );
}