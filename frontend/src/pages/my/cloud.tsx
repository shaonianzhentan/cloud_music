import React, { useEffect } from 'react';
import styles from './cloud.less';
import { ha, IPersonalized } from '../../http/cloudMusic'

export default function Page() {

  useEffect(() => {

    ha.neteaseCloudMusic('/user/cloud').then(res => {
      console.log(res)
    })

    return () => {

    }
  }, [])

  return (
    <div>
      <h1 className={styles.title}>Page my/cloud</h1>
    </div>
  );
}
