import logging
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_rsi_vectorized(data, period):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def fetch_and_calculate_rsi(symbol, period, threshold):
    try:
        #logging.info(f"Fetching data for {symbol}")
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1mo")
        
        if data.empty or 'Close' not in data.columns:
            logging.warning(f"Insufficient data for {symbol}")
            return None
        
        close_data = data['Close']
        rsi = calculate_rsi_vectorized(close_data, period)
        rsi_last = rsi.iloc[-1]
        
        if rsi_last > threshold:
            return symbol, rsi_last
    except Exception as e:
        logging.error(f"Error processing {symbol}: {str(e)}", exc_info=True)
    
    return None

def rsiFilter(symbols, rsi_period, rsi_threshold):
    results = {}
    num_workers = min(32, (multiprocessing.cpu_count() + 4))

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(fetch_and_calculate_rsi, symbol, rsi_period, rsi_threshold) for symbol in symbols]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                symbol, rsi_value = result
                results[symbol] = rsi_value
    
    return results


# Example usage
if __name__ == "__main__":
    symbols = ['BRK-B', 'LLY', 'TSM', 'JPM', 'NVO', 'WMT', 'V', 'XOM', 'UNH', 'MA', 'PG', 'ORCL', 'JNJ', 'HD', 'BAC', 'MRK', 'ABBV', 'CVX', 'KO', 'CRM', 'SAP', 'SHEL', 'NVS', 'TMO', 'ACN', 'WFC', 'MCD', 'DHR', 'ABT', 'GE', 'AXP', 'BX', 'DIS', 'CAT', 'IBM', 'PFE', 'PM', 'MS', 'VZ', 'BABA', 'TTE', 'HSBC', 'GS', 'NOW', 'SPGI', 'NEE', 'UNP', 'HDB', 'UL', 'UBER', 'BHP', 'RTX', 'LOW', 'T', 'MUFG', 'COP', 'SYK', 'ETN', 'TJX', 'PGR', 'BUD', 'UPS', 'C', 'PLD', 'ELV', 'SCHW', 'BSX', 'LMT', 'NKE', 'SONY', 'BA', 'RIO', 'MMC', 'ANET', 'CB', 'KKR', 'DE', 'IBN', 'TD', 'MDT', 'UBS', 'AMT', 'BP', 'CI', 'FI', 'PBR-A', 'PBR', 'DELL', 'SMFG', 'INFY', 'WM', 'SO', 'BMY', 'ICE', 'HCA', 'RELX', 'MO', 'DUK', 'ZTS', 'MCO', 'SCCO', 'SHW', 'SHOP', 'CL', 'GSK', 'GD', 'APH', 'ENB', 'CP', 'CNI', 'BN', 'TT', 'CNQ', 'FDX', 'BTI', 'CMG', 'CVS', 'ITW', 'EOG', 'EQNR', 'DEO', 'SLB', 'APO', 'PNC', 'USB', 'TGT', 'EMR', 'BDX', 'FCX', 'MSI', 'EPD', 'AON', 'WELL', 'NOC', 'BMO', 'BBVA', 'NU', 'STLA', 'CARR', 'ING', 'PLTR', 'NGG', 'PSX', 'TFC', 'MPC', 'DHI', 'MMM', 'SPOT', 'BNS', 'GM', 'CRH', 'COF', 'F', 'APD', 'ET', 'HLT', 'AMX', 'WMB', 'NEM', 'OXY', 'AFL', 'MET', 'PSA', 'EW', 'HMC', 'NSC', 'SPG', 'AIG', 'DLR', 'O', 'SU', 'SRE', 'OKE', 'URI', 'VLO', 'KMB', 'KMI', 'CM', 'BK', 'JCI', 'MFC', 'TRV', 'LEN', 'WCN', 'TEL', 'VALE', 'HUM', 'HES', 'ALL', 'GEV', 'CCI', 'LHX', 'COR', 'ALC', 'PRU', 'IQV', 'STZ', 'BCS', 'MPLX', 'SNOW', 'D', 'RCL', 'TRP', 'TAK', 'FERG', 'SQ', 'FIS', 'LNG', 'IR', 'OTIS', 'MSCI', 'AME', 'CMI', 'KR', 'PWR', 'NUE', 'PCG', 'A', 'SE', 'HSY', 'DOW', 'CTVA', 'GLW', 'PEG', 'STM', 'AEM', 'HPQ', 'CVE', 'CPNG', 'SYY', 'WDS', 'EL', 'YUM', 'GIS', 'CNC', 'EXR', 'DFS', 'MLM', 'KVUE', 'VMC', 'XYL', 'DD', 'DB', 'EFX', 'VRT', 'HWM', 'ED', 'GOLD', 'VICI', 'LYB', 'ADM', 'ROK', 'LVS', 'TRGP', 'RMD', 'CBRE', 'VEEV', 'HIG', 'PPG', 'BCE', 'WAB', 'RKT', 'HAL', 'ARES', 'DVN', 'IRM', 'EIX', 'OWL', 'MTB', 'DAL', 'PINS', 'VST', 'WPM', 'DG', 'FTV', 'EQR', 'HPE', 'NET', 'BRO', 'PHM', 'RBLX', 'WEC', 'GPN', 'PUK', 'STT', 'IFF', 'NTR', 'DOV', 'SW', 'PHG', 'HUBS', 'CHD', 'VLTO', 'ROL', 'KEYS', 'TME', 'SNAP', 'BR', 'ASX', 'ETR', 'TECK', 'TU', 'CAH', 'WST', 'CCL', 'QSR', 'FE', 'RJF', 'ZBH', 'WY', 'EC', 'INVH', 'PBA', 'ARE', 'LYV', 'ES', 'VTR', 'PPL', 'TSN', 'GDDY', 'BF-B', 'CCJ', 'LDOS', 'RF', 'IOT', 'SYF', 'RCI', 'AEE', 'AER', 'CTRA', 'WRB', 'PSTG', 'MKC', 'K', 'BLDR', 'WSM', 'GPC', 'TEVA', 'TLK', 'BBY', 'BALL', 'APTV', 'CFG', 'MT', 'ATO', 'CNP', 'CMS', 'TS', 'LH', 'AVY', 'CRBG', 'BAX', 'OMC', 'BAM', 'BEKE', 'TXT', 'EXPD', 'HRL', 'DRI', 'MOH', 'DKS', 'LUV', 'CLX', 'DGX', 'WES', 'ZTO', 'IP', 'BURL', 'MAS', 'NRG', 'RTO', 'BG', 'MRO', 'EQT', 'SUI', 'VIK', 'TRU', 'CE', 'TOST', 'CVNA', 'KEY', 'DOC', 'GFI', 'RBA', 'FNF', 'RPM', 'AMCR', 'DPZ', 'KIM', 'GFL', 'AVTR', 'CAG', 'GGG', 'UDR', 'NI', 'CPB', 'TOL', 'AGR', 'MGM', 'EQH', 'RVTY', 'SWK', 'AMH', 'XPO', 'THC', 'DT', 'CF', 'AOS', 'ONON', 'WPC', 'CNH', 'USFD', 'NVT', 'JBL', 'MGA', 'ALLY', 'EDU', 'ELS', 'KMX', 'OVV', 'AES', 'BEN', 'SJM', 'EPAM', 'ACM', 'PR', 'JNPR', 'BJ', 'CPT', 'FTI', 'YUMC', 'GWRE', 'AU', 'ACI', 'ESTC', 'YPF', 'LW', 'EMN', 'JEF', 'IPG', 'SQM', 'TAP', 'RDDT', 'WTRG', 'ALLE', 'ALB', 'SCI', 'CHWY', 'UHS', 'CUBE', 'REXR', 'GME', 'SBS', 'BXP', 'RL', 'CTLT', 'APG', 'BIRK', 'PFGC', 'PCOR', 'UNM', 'NLY', 'SNX', 'FND', 'SN', 'CNM', 'TTC', 'TWLO', 'GMED', 'SKX', 'GNRC', 'TPR', 'AR', 'ELF', 'MOS', 'QGEN', 'CCK', 'SOLV', 'PAYC', 'DINO', 'KBR', 'CAVA', 'NYT', 'FHN', 'OHI', 'FBIN', 'TPX', 'TREX', 'ORI', 'ARMK', 'EHC', 'HESM', 'INFA', 'X', 'GPK', 'TKO', 'WAL', 'DAY', 'NCLH', 'NNN', 'SF', 'WBS', 'BBWI', 'FLR', 'EDR', 'GPS', 'GL', 'COLD', 'RRC', 'MHK', 'ANF', 'KNX', 'ALV', 'HRB', 'MTDR', 'AXTA', 'AGCO', 'BRX', 'BWA', 'NOV', 'IVZ', 'VIPS', 'ALSN', 'ATI', 'LEVI', 'DTM', 'STAG', 'MLI', 'AM', 'VOYA', 'CIEN', 'S', 'CLF', 'FMC', 'AGI', 'FR', 'CIVI', 'PATH', 'CCCS', 'RHI', 'RYAN', 'SUM', 'LEA', 'CMA', 'CLS', 'KT', 'SNV', 'NE', 'SMAR', 'KVYO', 'FLS', 'PLNT', 'ESI', 'HR', 'ADC', 'AZEK', 'TRNO', 'BRBR', 'TAL', 'LPX', 'ESNT', 'U', 'JXN', 'ENLC', 'STWD', 'KD', 'VFC', 'ELAN', 'MTG', 'W', 'MUR', 'AA', 'VNT', 'BROS', 'SQSP', 'KBH', 'G', 'OBDC', 'WH', 'MOD', 'CRS', 'DAR', 'VVV', 'CADE', 'ST', 'WHR', 'OLN', 'FSK', 'BILL', 'PVH', 'FRO', 'AS', 'BYD', 'VAL', 'RITM', 'MNSO', 'AWI', 'HOMB', 'OGN', 'VNO', 'LNC', 'MDU', 'ETRN', 'ZWS', 'DOCS', 'EPRT', 'AL', 'NFG', 'HXL', 'SM', 'RDN', 'THO', 'FNB', 'KRG', 'BC', 'SEE', 'BEPC', 'CWEN', 'NSA', 'ERJ', 'UGI', 'FUN', 'BIPC', 'GBCI', 'CWAN', 'ALK', 'POR', 'MGY', 'RH', 'HOG', 'MSM', 'FLO', 'PII', 'DNB', 'ZETA', 'GTES', 'M', 'MC', 'PBF', 'HGV', 'PAGS', 'TPH', 'IRT', 'FOUR', 'IGT', 'WU', 'STNG', 'TEX', 'HIMS', 'LTH', 'QTWO', 'KRC', 'HRI', 'SPR', 'AEO', 'NOG', 'BVN', 'AX', 'SLG', 'HUN', 'CNX', 'LAZ', 'BOX', 'SMG', 'NYCB', 'SIG', 'PRGO', 'BOOT', 'PWSC', 'HP', 'CUZ', 'ALE', 'AROC', 'APLE', 'PRKS', 'HASI', 'JWN', 'LBRT', 'HCC', 'CC', 'AAP', 'MAC', 'RXO', 'ASB', 'FBP', 'TNL', 'HTGC', 'DV', 'DXC', 'BXMT', 'ENV', 'AI', 'EPR', 'EGO', 'PRMW', 'VSH', 'CNO', 'SITC', 'BNL', 'ASAN', 'YETI', 'BE', 'SHAK', 'BHVN', 'PK', 'MWA', 'CRK', 'OSCR', 'CDP', 'TDC', 'LXP', 'BUR', 'RNG', 'HIW', 'EAT', 'DOCN', 'CWK', 'NOMD', 'INSW', 'MODG', 'BTU', 'SG', 'NVST', 'BKU', 'XPRO', 'WOLF', 'CSTM', 'BOH', 'TGNA', 'HAYW', 'CNK', 'OII', 'NEP', 'DBRG', 'WNS', 'OUT', 'AMK', 'ABR', 'DEI', 'TROX', 'CVI', 'MIR', 'BANC', 'CALX', 'FL', 'KGS', 'AIR', 'MP', 'UE', 'PFS', 'RSI', 'EVH', 'KSS', 'ADNT', 'TDS', 'CRI', 'VSTO', 'GEO', 'TALO', 'VZIO', 'CRGY', 'MBC', 'VYX', 'SHO', 'ZIM', 'RAMP', 'LSPD', 'EQC', 'AKR', 'PD', 'JBI', 'DHT', 'HLX', 'SFL', 'WRBY', 'YOU', 'VGR', 'ASPN', 'ESRT', 'OI', 'CMRE', 'VET', 'DAN', 'LEG', 'FCF', 'PEB', 'HE', 'VSTS', 'DO', 'WT', 'CXW', 'LMND', 'SPHR', 'SCS', 'ARLO', 'DNOW', 'LADR', 'ARI', 'JBGS', 'JMIA', 'VRE', 'KW', 'VSCO', 'DK', 'KLG', 'DEA', 'REVG', 'PARR', 'JELD', 'SILA', 'RCUS', 'PMT', 'CAL', 'GES', 'RVLV', 'SLCA', 'UTZ', 'SBH', 'LC', 'MFA', 'OMI', 'HLF', 'WWW', 'MEG', 'DQ', 'WTTR', 'EFC', 'ARR', 'ATEN', 'UTI', 'SMR', 'MTUS', 'SBOW', 'SOC', 'MAX', 'CWH', 'IMAX', 'DX', 'SXC', 'GNK', 'ASC', 'FVRR', 'CATX', 'ECC', 'PFLT', 'DESP', 'AHR', 'OUST', 'BYON', 'EBS', 'XPOF', 'NUS', 'ORN', 'SOI', 'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'AVGO', 'COST', 'ASML', 'NFLX', 'AMD', 'ADBE', 'AZN', 'PEP', 'QCOM', 'LIN', 'TMUS', 'CSCO', 'TXN', 'AMAT', 'AMGN', 'INTU', 'PDD', 'ARM', 'ISRG', 'CMCSA', 'INTC', 'HON', 'VRTX', 'SNY', 'MU', 'LRCX', 'ADI', 'KLAC', 'PANW', 'ADP', 'ABNB', 'GILD', 'SNPS', 'MDLZ', 'SBUX', 'CDNS', 'NXPI', 'CME', 'MAR', 'CSX', 'COIN', 'CRWD', 'PYPL', 'WDAY', 'CEG', 'MRVL', 'NTES', 'PCAR', 'ADSK', 'MNST', 'CPRT', 'MCHP', 'AEP', 'TTD', 'ROST', 'MRNA', 'SMCI', 'TEAM', 'CHTR', 'FTNT', 'KDP', 'DXCM', 'PAYX', 'DASH', 'ODFL', 'MPWR', 'DDOG', 'KHC', 'IDXX', 'FAST', 'EA', 'JD', 'CTSH', 'GEHC', 'FANG', 'NDAQ', 'ACGL', 'EXC', 'BKR', 'LULU', 'CCEP', 'BIDU', 'ON', 'BIIB', 'MSTR', 'CDW', 'GFS', 'XEL', 'CSGP', 'TCOM', 'ALNY', 'TSCO', 'FWONK', 'ZS', 'FITB', 'APP', 'EBAY', 'NTAP', 'TTWO', 'TW', 'TROW', 'TER', 'WDC', 'FSLR', 'DLTR', 'STX', 'HBAN', 'PTC', 'HOOD', 'LI', 'RYAAY', 'ENTG', 'STLD', 'PFG', 'MBLY', 'SWKS', 'CHKP', 'CINF', 'ALGN', 'ILMN', 'ULTA', 'MDB', 'HOLX', 'COO', 'ZM', 'GMAB', 'DKNG', 'TPG', 'EXPE', 'RIVN', 'JBHT', 'CG', 'SSNC', 'FOXA', 'WMG', 'BMRN', 'LPLA', 'GEN', 'UAL', 'OKTA', 'NWSA', 'BSY', 'AKAM', 'INCY', 'NBIX', 'ENPH', 'LOGI', 'LNT', 'TRMB', 'VTRS', 'MANH', 'SRPT', 'PAA', 'GLPI', 'IBKR', 'NTRA', 'ARCC', 'RPRX', 'EVRG', 'HST', 'REG', 'INSM', 'TECH', 'NTNX', 'Z', 'LKQ', 'QRVO', 'FLEX', 'APA', 'TXRH', 'DOCU', 'EWBC', 'COHR', 'CELH', 'CHRD', 'LEGN', 'CHK', 'CHRW', 'FTAI', 'CHDN', 'FFIV', 'HTHT', 'AMKR', 'XP', 'MMYT', 'WBA', 'WFRD', 'BRKR', 'CART', 'WYNN', 'LNW', 'AFRM', 'PCVX', 'MTCH', 'HSIC', 'ROKU', 'MKSI', 'EXAS', 'SEIC', 'CGNX', 'GTLB', 'SFM', 'HAS', 'PAAS', 'CBSH', 'ALAB', 'ROIV', 'PARA', 'LSCC', 'CROX', 'ITCI', 'CFLT', 'LNTH', 'WSC', 'CERE', 'RVMD', 'CZR', 'GNTX', 'DBX', 'ALTR', 'VNOM', 'DRS', 'AGNC', 'IONS', 'LSXMK', 'BPMC', 'ZION', 'ETSY', 'BZ', 'LBTYK', 'LBTYA', 'TEM', 'AAL', 'HCP', 'MIDD', 'HALO', 'RMBS', 'NXT', 'WTFC', 'FYBR', 'CHX', 'DJT', 'CYTK', 'EXEL', 'HQY', 'MARA', 'BILI', 'MAT', 'ONB', 'BECN', 'ACHC', 'OLLI', 'VERX', 'GLBE', 'VKTX', 'COOP', 'RCM', 'ALGM', 'EXLS', 'XRAY', 'SRCL', 'OPCH', 'SATS', 'VRNS', 'NFE', 'FFIN', 'TENB', 'OZK', 'VRRM', 'SLM', 'PEGA', 'UBSI', 'CAMT', 'SIGI', 'BBIO', 'COLB', 'LYFT', 'CRDO', 'CRSP', 'RDNT', 'NVEI', 'IAC', 'APLS', 'ACIW', 'ACLS', 'RNA', 'FIVE', 'URBN', 'ZI', 'PECO', 'DYN', 'CRNX', 'ALKS', 'STNE', 'ABCB', 'CLSK', 'GBDC', 'FROG', 'PTEN', 'IMVT', 'AXSM', 'RARE', 'BRZE', 'ASO', 'SYM', 'PAGP', 'FRSH', 'GH', 'SBRA', 'NCNO', 'RUN', 'LITE', 'SLAB', 'TRMD', 'SHC', 'FULT', 'CORT', 'NEOG', 'GLNG', 'SGRY', 'ARWR', 'RIOT', 'WEN', 'RRR', 'EBC', 'SMPL', 'ASTS', 'GT', 'DNLI', 'SRAD', 'TWST', 'SHOO', 'FIVN', 'KTOS', 'NARI', 'ADMA', 'FHB', 'TGTX', 'IRDM', 'ACVA', 'QFIN', 'FOLD', 'RYTM', 'WBTN', 'ACAD', 'PRIM', 'LIVN', 'FLNC', 'FTDR', 'BL', 'PENN', 'WAFD', 'MORF', 'TNDM', 'SBLK', 'FUTU', 'SWTX', 'CVBF', 'CLBT', 'GOGL', 'PPBI', 'CERT', 'VIRT', 'PGNY', 'KYMR', 'AVDX', 'RELY', 'ENVX', 'AY', 'TBBK', 'APPN', 'MYGN', 'TRIP', 'RPD', 'IART', 'NTLA', 'UPST', 'NATL', 'VECO', 'FTRE', 'CLDX', 'QDEL', 'PRVA', 'ATAT', 'WERN', 'CGON', 'PYCR', 'ARHS', 'CRTO', 'BEAM', 'TTMI', 'FLYW', 'PDCO', 'RCKT', 'TXG', 'DRVN', 'GDS', 'EXPI', 'IREN', 'SMTC', 'MGNI', 'PTGX', 'VRNT', 'NVAX', 'GPCR', 'MXL', 'NMRK', 'PINC', 'EWTX', 'BTSG', 'GO', 'NVCR', 'CPRX', 'CAKE', 'SNDX', 'ARVN', 'AVPT', 'CORZ', 'ZLAB', 'VSAT', 'AKRO', 'NEO', 'MIRM', 'VRNA', 'NMRA', 'HUT', 'DNUT', 'VCYT', 'EXTR', 'SONO', 'ROIC', 'NAVI', 'BLMN', 'NWBI', 'SDGR', 'IAS', 'POWL', 'SUPN', 'ARRY', 'VITL', 'HOLI', 'BTDR', 'AVDL', 'KURA', 'HOPE', 'UPWK', 'ATEC', 'PLAY', 'SEDG', 'INMD', 'XRX', 'CENX', 'HLIT', 'OCSL', 'COCO', 'MRTN', 'LBPH', 'DVAX', 'NRIX', 'VIR', 'PZZA', 'ACMR', 'HELE', 'DAWN', 'NTCT', 'SGH', 'ICHR', 'AOSL', 'GIII', 'GCT', 'ATRC', 'CGEM', 'OPRA', 'SILK', 'PGY', 'GPRE', 'CSIQ', 'AMSC', 'HIBB', 'EYE', 'OCFC', 'TARS', 'CBRL', 'CDNA', 'VRDN', 'PCRX', 'EVER', 'FDMT', 'BJRI', 'ALGT', 'EMBC', 'LBAI', 'LQDA', 'OLMA', 'STOK', 'EH', 'SAGE', 'PHAT', 'GRPN', 'FWRD', 'CHUY', 'CELC', 'SAVA', 'EZPW', 'AEHR', 'MAGS', 'RILY', 'GRAL', 'NNE', 'IMMR', 'LXEO', 'ZNTE', 'IRBT']
    rsi_period = 14
    rsi_threshold = 92
    
    filtered_symbols = rsiFilter(symbols, rsi_period, rsi_threshold)
    print(filtered_symbols)
