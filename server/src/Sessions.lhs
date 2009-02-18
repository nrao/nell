> module Sessions where

> import Control.Monad.Trans                   (liftIO)
> import Data.Record.Label
> import Data.List                             (intercalate)
> import Data.Maybe                            (maybeToList)
> import Database.HDBC
> import Database.HDBC.PostgreSQL              (Connection)
> import Json
> import List
> import Network.Protocol.Http
> import Network.Protocol.Uri
> import Network.Salvia.Handlers.Error         (hError)
> import Network.Salvia.Handlers.MethodRouter  (hMethodRouter)
> import Network.Salvia.Httpd
> import qualified Data.ByteString.Lazy.Char8 as L

> data Session = Session {
>     session_id :: Int
>   , fields     :: [(String, String)]
>   }

> instance JSON Session where
>     readJSON = jsonToSession
>     showJSON = sessionToJson

> jsonToSession _ = undefined

> sessionToJson (Session sid fields) = makeObj $
>     ("id", showJSON sid) : [(key, showJSON value) | (key, value) <- fields]

> sessionsHandler     :: Connection -> Handler ()
> sessionsHandler cnn = hMethodRouter [
>       (GET,  listSessions cnn)
>     , (POST, handlePost cnn)
>     ] $ hError NotFound

> -- GET /sessions
> listSessions cnn = do
>     sessions <- liftIO $ listSessions' cnn
>     jsonHandler $ makeObj [("sessions", showJSON sessions)]

> listSessions' cnn = do
>     rst <- quickQuery' cnn "SELECT id FROM sessions" []
>     mapM (readSession cnn) [fromSql sid | [sid] <- rst]

> readSession cnn sid = do
>     rst <- quickQuery' cnn "SELECT key, value FROM fields where session_id = ?" [toSql sid]
>     return $ Session sid [(fromSql key, fromSql value) | [key, value] <- rst]

> handlePost cnn = do
>     bytes <- contents
>     let params = maybe [] id $ bytes >>= parseQueryParams . L.unpack
>     case lookup' Nothing "_method" params of
>         Nothing       -> newSession cnn params
>         Just "delete" -> deleteSession cnn params
>         Just "put"    -> saveSession cnn params

> -- POST /sessions
> newSession cnn params = do
>     [[sid]] <- liftIO $ newSession' cnn
>     saveSession' cnn (fromSql sid) params

> newSession' cnn = withTransaction cnn $ \cnn -> do
>     run cnn "INSERT INTO sessions(dummy) values(0)" []
>     quickQuery' cnn "SELECT CURRVAL('sessions_id_seq')" []

> -- PUT /sessions/:id
> saveSession cnn params = do
>     '/' : sid <- getM $ path % uri % request
>     saveSession' cnn (read sid) params

> saveSession' cnn sid params = do      
>     liftIO $ saveSession'' cnn sid params'
>     session <- liftIO $ readSession cnn sid
>     jsonHandler session
>   where
>     params' = [(key, value) | (key, Just value) <- params, not $ key `elem` ["_method", "id"]]

> saveSession'' :: Connection -> Int -> [(String, String)] -> IO ()
> saveSession'' cnn sid params = withTransaction cnn $ \cnn -> do
>     run cnn "DELETE FROM fields WHERE session_id = ?" [toSql sid]
>     flip mapM_ params $ \(key, value) ->
>         run cnn "INSERT INTO fields(session_id, key, value) VALUES(?, ?, ?)" [toSql sid, toSql key, toSql value]

> updateQuery :: Connection -> String -> [(String, String)] -> IO ()
> updateQuery cnn key slots = withTransaction cnn $ \cnn -> do
>     sRun cnn query $ map (Just . snd) slots ++ [Just key]
>     return ()
>   where
>     query  = "UPDATE sessions SET " ++ query' ++ " WHERE id = ?"
>     query' = intercalate ", " $ [name ++ " = ?" | (name, _) <- slots]

> -- DELETE /sessions/:id
> deleteSession cnn _ = do
>     '/' : sid <- getM $ path % uri % request
>     liftIO $ deleteSession' cnn (read sid)
>     jsonHandler $ makeObj [("success", showJSON "ok")]

> deleteSession' :: Connection -> Int -> IO ()
> deleteSession' cnn sid = withTransaction cnn $ \cnn -> do
>     run cnn "DELETE FROM fields WHERE session_id = ?" [toSql sid]
>     run cnn "DELETE FROM sessions WHERE id = ?" [toSql sid]
>     return ()
