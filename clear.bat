@echo off
if exist "C:\laragon\www\NodeCash\node\NODECASH-BR\data" (
    rmdir "C:\laragon\www\NodeCash\node\NODECASH-BR\data" /s /q
)

if exist "C:\laragon\www\NodeCash\node\NODECASH-RS\data" (
    rmdir "C:\laragon\www\NodeCash\node\NODECASH-RS\data" /s /q
)

if exist "C:\laragon\www\NodeCash\node\NODECASH-SC\data" (
    rmdir "C:\laragon\www\NodeCash\node\NODECASH-SC\data" /s /q
)

if exist "C:\laragon\www\NodeCash\node\NODECASH-PR\data" (
    rmdir "C:\laragon\www\NodeCash\node\NODECASH-PR\data" /s /q
)

if exist "C:\laragon\www\NodeCash\node\NODECASH-SP\data" (
    rmdir "C:\laragon\www\NodeCash\node\NODECASH-SP\data" /s /q
)

echo finalizado.
