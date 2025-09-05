import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                Python 3.12.8
              </li>
              <li className={styles.textItem}>
                Django 5.2.5
              </li>
              <li className={styles.textItem}>
                Django REST Framework 3.16
              </li>
              <li className={styles.textItem}>
                Аутентификацция по токену - Djoser 2.3.3
              </li>
              <li className={styles.textItem}>
                Контейнеризация и оркестрирование - Docker 28.3.3
              </li>
              <li className={styles.textItem}>
                Веб-сервер Nginx 1.25
              </li>
              <li className={styles.textItem}>
                База данных - PostgreSQL 14
              </li>
              <li className={styles.textItem}>
                Контроль версий - Git 2.48.1
              </li>
              <li className={styles.textItem}>
                Автоматизация CI/CD - workflow GitHub Actions
              </li>
              <li className={styles.textItem}>
                Размещение на сервере под управлением Linux OS
              </li>             
              
            </ul>
          </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies

