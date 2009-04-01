#! /usr/bin/env runhaskell

> module Main where

> import Control.Concurrent.STM              (atomically, newTVar)
> import Control.Monad.Trans                 (liftIO)
> import Database.HDBC                       (disconnect, handleSqlError)
> import Database.HDBC.PostgreSQL            (connectPostgreSQL)
> import Network.Salvia.Handlers.Default     (hDefault)
> import Network.Salvia.Handlers.Error       (hError)
> import Network.Salvia.Handlers.PathRouter  (hPrefixRouter)
> import Network.Salvia.Handlers.Session     (SessionHandler, mkSessions)
> import Network.Protocol.Http               (Status(..))
> import Network.Salvia.Httpd
> import Network.Socket                      (inet_addr)
> import Sessions

> -- set DATABASE to name of database
> connect = handleSqlError $ connectPostgreSQL "dbname=dss_mclark user=dss"

> main = do
>     addr <- inet_addr "127.0.0.1"
>     cfg  <- defaultConfig
>     let cfg' = cfg {
>         hostname   = "localhost"
>       , email      = "nubgames@gmail.com"
>       , listenAddr = addr
>       -- set CCCC to UI server port
>       , listenPort = 9002
>       }
>     mkHandler >>= start cfg'

> discardSession           :: Handler a -> SessionHandler () a
> discardSession handler _ = handler

> mkHandler = do
>     counter  <- atomically $ newTVar 0
>     sessions <- mkSessions
>     return $ hDefault counter sessions handler

> handler = discardSession $ do
>     cnn <- liftIO connect
>     hPrefixRouter [
>           ("/sessions", sessionsHandler cnn)
>       ] $ hError NotFound
>     liftIO $ disconnect cnn
