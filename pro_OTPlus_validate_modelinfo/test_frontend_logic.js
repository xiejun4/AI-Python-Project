// 测试前端验证逻辑
const fs = require('fs');

// 读取 XML 文件内容
const xmlContent = fs.readFileSync('ModelInfoFile_Beryl.xml', 'utf-8');

// 模拟浏览器的 DOMParser
const { JSDOM } = require('jsdom');
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
global.DOMParser = dom.window.DOMParser;

// 复制前端的验证函数
function validateRfpathFormat(rfpath) {
    try {
        const connPart = rfpath.split('CONN')[1].split('_TO_TESTSET')[0];
        const connNumber = parseInt(connPart);
        
        let rfType = '';
        if (rfpath.includes('MAIN_RF')) {
            rfType = 'MAIN_RF';
        } else if (rfpath.includes('ALT1_RF')) {
            rfType = 'ALT1_RF';
        } else if (rfpath.includes('DIRECT_RF')) {
            rfType = 'DIRECT_RF';
        } else {
            return {
                valid: false,
                errorParts: [rfpath.split('_TO_TESTSET')[1] || rfpath],
                correctHint: 'RF 类型必须是 MAIN_RF、ALT1_RF 或 DIRECT_RF'
            };
        }
        
        if (rfType === 'MAIN_RF') {
            const allowedConn = new Set([1, 3, 4, 6, 7, 8, 11, 12, 13, 14, 15]);
            if (!allowedConn.has(connNumber)) {
                return {
                    valid: false,
                    errorParts: [`CONN${connNumber}`, 'MAIN_RF'],
                    correctHint: 'MAIN_RF 的 CONN 数值必须在 {1, 3, 4, 6, 7, 8, 11, 12, 13, 14, 15} 中'
                };
            }
        } else if (rfType === 'ALT1_RF') {
            const allowedConn = new Set([2, 5, 9, 10]);
            if (!allowedConn.has(connNumber)) {
                return {
                    valid: false,
                    errorParts: [`CONN${connNumber}`, 'ALT1_RF'],
                    correctHint: 'ALT1_RF 的 CONN 数值必须在 {2, 5, 9, 10} 中'
                };
            }
        } else if (rfType === 'DIRECT_RF') {
            const allowedConn = new Set();
            for (let i = 100; i < 1000; i += 100) {
                allowedConn.add(i);
            }
            if (!allowedConn.has(connNumber)) {
                return {
                    valid: false,
                    errorParts: [`CONN${connNumber}`, 'DIRECT_RF'],
                    correctHint: 'DIRECT_RF 的 CONN 数值必须是 100, 200, ..., 900'
                };
            }
        }
        
        return {
            valid: true,
            errorParts: [],
            correctHint: ''
        };
    } catch (e) {
        return {
            valid: false,
            errorParts: [rfpath],
            correctHint: 'Rfpath_name 格式无效'
        };
    }
}

// 测试 XML 解析和验证
function testValidation() {
    try {
        // 解析 XML
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlContent, "text/xml");
        
        // 提取产品和模型信息
        const products = [];
        let productElements = xmlDoc.getElementsByTagName("Product");
        
        // 如果没有找到 Product 元素，尝试使用命名空间
        if (productElements.length === 0) {
            // 查找所有元素，然后过滤出 Product 元素
            const allElements = xmlDoc.getElementsByTagName("*");
            // 使用更兼容的方式处理 HTMLCollection
            const elementsArray = [];
            for (let i = 0; i < allElements.length; i++) {
                elementsArray.push(allElements[i]);
            }
            productElements = elementsArray.filter(element => 
                element.localName === "Product"
            );
        }
        
        for (let i = 0; i < productElements.length; i++) {
            const productElement = productElements[i];
            const productName = productElement.getAttribute("name");
            let modelElements = productElement.getElementsByTagName("Model");
            
            // 如果没有找到 Model 元素，尝试使用命名空间
            if (modelElements.length === 0) {
                // 查找所有子元素，然后过滤出 Model 元素
                const allChildElements = productElement.getElementsByTagName("*");
                // 使用更兼容的方式处理 HTMLCollection
                const elementsArray = [];
                for (let i = 0; i < allChildElements.length; i++) {
                    elementsArray.push(allChildElements[i]);
                }
                modelElements = elementsArray.filter(element => 
                    element.localName === "Model"
                );
            }
            
            const productResult = {
                product: productName,
                results: []
            };
            
            for (let j = 0; j < modelElements.length; j++) {
                const modelElement = modelElements[j];
                const modelName = modelElement.getAttribute("name");
                let bandElements = modelElement.getElementsByTagName("Band");
                
                // 如果没有找到 Band 元素，尝试使用命名空间
                if (bandElements.length === 0) {
                    // 查找所有子元素，然后过滤出 Band 元素
                    const allChildElements = modelElement.getElementsByTagName("*");
                    // 使用更兼容的方式处理 HTMLCollection
                    const elementsArray = [];
                    for (let i = 0; i < allChildElements.length; i++) {
                        elementsArray.push(allChildElements[i]);
                    }
                    bandElements = elementsArray.filter(element => 
                        element.localName === "Band"
                    );
                }
                
                const valid = [];
                const invalid = [];
                
                for (let k = 0; k < bandElements.length; k++) {
                    const bandElement = bandElements[k];
                    const bandName = bandElement.getAttribute("name");
                    const rfpath = bandElement.getAttribute("Rfpath_name");
                    const devicePath = bandElement.getAttribute("device_path");
                    
                    if (rfpath) {
                        // 验证 Rfpath_name 格式
                        const validationResult = validateRfpathFormat(rfpath);
                        
                        if (validationResult.valid) {
                            valid.push({
                                band: bandName,
                                rfpath: rfpath,
                                device_path: devicePath
                            });
                        } else {
                            invalid.push({
                                band: bandName,
                                rfpath: rfpath,
                                device_path: devicePath,
                                reason: `Invalid Rfpath_name format: ${rfpath}`,
                                errorParts: validationResult.errorParts,
                                correctHint: validationResult.correctHint
                            });
                        }
                    }
                }
                
                productResult.results.push({
                    model: modelName,
                    valid: valid,
                    invalid: invalid
                });
            }
            
            products.push(productResult);
        }
        
        // 构建验证结果
        const result = {
            success: true,
            data: {
                results: products,
                allValid: products.every(p => 
                    p.results.every(r => r.invalid.length === 0)
                )
            }
        };
        
        // 输出验证结果
        console.log(JSON.stringify(result, null, 2));
    } catch (error) {
        console.error(`验证出错: ${error.message}`);
    }
}

// 运行测试
testValidation();